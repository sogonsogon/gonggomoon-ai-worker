from pydantic import BaseModel

from app.config.enums import JobType


class BaseJobMessage(BaseModel):
    id: int | None = None
    user_id: int
    job_type: JobType
    callback_url: str | None = None
    attempt_count: int = 1
    max_attempts: int = 3
