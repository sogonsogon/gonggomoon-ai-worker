from datetime import datetime, timezone
from typing import Optional

from app.application.dto.dto import BaseJobMessage
from app.core.enums import JobStatus, JobType
from app.application.ports.ports import CallbackPort, JobQueuePort
from app.worker.handlers import JobHandler


class WorkerExecutor:
    def __init__(
        self,
        handler: JobHandler,
        callback_client: CallbackPort,
        queue: Optional[JobQueuePort] = None,
    ) -> None:
        self.queue = queue
        self.handler = handler
        self.callback_client = callback_client

    # Cloud Tasks push 방식: 메시지를 직접 받아 처리합니다.
    # 처리 성공 시 콜백을 전송합니다.
    # 처리 실패 시:
    #   - max_attempts 미만이면 예외를 그대로 던져 HTTP 500을 반환 → Cloud Tasks가 재시도
    #   - max_attempts 이상이면 실패 콜백을 전송하고 정상 반환 → Cloud Tasks 재시도 중단
    def process_message(self, message: BaseJobMessage) -> None:
        try:
            callback_body = self.handler.handle(message)
            self._send_callback(message, callback_body)
        except Exception as exc:
            if message.attempt_count >= message.max_attempts:
                print(
                    f"Job {message.id} of type {message.job_type} failed after "
                    f"{message.max_attempts} attempts. Error: {exc}"
                )
                self._send_failure_callback(message, exc)
            else:
                print(
                    f"Job {message.id} of type {message.job_type} failed. "
                    f"Attempt {message.attempt_count}/{message.max_attempts}. Error: {exc}"
                )
                raise

    def _send_callback(self, message: BaseJobMessage, body: dict) -> None:
        if message.callback_url:
            self.callback_client.send(message.callback_url, body)

    def _send_failure_callback(self, message: BaseJobMessage, exc: Exception) -> None:
        if not message.callback_url:
            return

        failure_body = {
            "type": message.job_type.value,
            "id": message.id,
            "user_id": str(message.user_id),
            "status": JobStatus.FAILED.value,
            "result": None,
            "error": str(exc),
            "attempt_count": message.attempt_count,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        if message.job_type == JobType.EXPERIENCE_EXTRACTION:
            failure_body["result"] = [
                {
                    "extracted_experience_id": item.get("extracted_experience_id"),
                    "file_asset_id": item.get("file_asset_id"),
                }
                for item in message.file_asset_ids
            ]

        try:
            self.callback_client.send(message.callback_url, failure_body)
        except Exception as callback_exc:
            print(
                f"Failed to send failure callback for job {message.id} "
                f"of type {message.job_type}. Error: {callback_exc}"
            )
