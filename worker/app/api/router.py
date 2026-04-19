from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request

from app.application.container import worker_executor
from app.application.dto.dto import (
    BaseJobMessage,
    ExtractedExperienceMessage,
    InterviewStrategyGenerationMessage,
    PortfolioStrategyGenerationMessage,
)
from app.core.config import get_settings
from app.core.enums import JobType

router = APIRouter()
settings = get_settings()


def _parse_message(data: dict) -> BaseJobMessage:
    job_type = data.get("job_type")

    if job_type == JobType.EXPERIENCE_EXTRACTION.value:
        return ExtractedExperienceMessage.model_validate(data)
    if job_type == JobType.PORTFOLIO_STRATEGY_GENERATION.value:
        return PortfolioStrategyGenerationMessage.model_validate(data)
    if job_type == JobType.INTERVIEW_STRATEGY_GENERATION.value:
        return InterviewStrategyGenerationMessage.model_validate(data)
    if job_type == JobType.POST_ANALYSIS.value:
        return BaseJobMessage.model_validate(data)

    raise ValueError(f"Unsupported job_type: {job_type}")


# Cloud Tasks가 호출하는 엔드포인트입니다.
# X-Internal-Api-Key 헤더로 인증합니다.
# X-CloudTasks-TaskRetryCount 헤더로 현재 재시도 횟수를 받아 attempt_count에 반영합니다.
# 처리 성공 시 200을 반환하고, 처리 실패 시 500을 반환하여 Cloud Tasks가 재시도하도록 합니다.
# max_attempts를 초과한 경우 실패 콜백을 전송하고 200을 반환하여 Cloud Tasks 재시도를 중단합니다.
@router.post("/tasks/execute", status_code=200)
async def execute_task(
    request: Request,
    x_internal_api_key: Annotated[str | None, Header()] = None,
    x_cloudtasks_taskretrycount: Annotated[str | None, Header()] = None,
) -> dict:
    if x_internal_api_key != settings.internal_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Cloud Tasks가 제공하는 재시도 횟수(0-indexed)를 attempt_count(1-indexed)로 변환하여 반영
    if x_cloudtasks_taskretrycount is not None:
        body["attempt_count"] = int(x_cloudtasks_taskretrycount) + 1

    try:
        message = _parse_message(body)
    except (ValueError, Exception) as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    try:
        worker_executor.process_message(message)
    except Exception as e:
        print(f"Job {message.id} (type={message.job_type}) failed: {e}")
        raise HTTPException(status_code=500, detail=f"Job processing failed: {str(e)}")

    return {"status": "ok", "job_id": message.id}
