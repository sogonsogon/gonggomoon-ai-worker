from typing import List
from typing_extensions import Annotated
from pydantic import BaseModel, Field

from app.config.enums import JobType
from app.task.schema import BaseJobMessage


# --- 작업 메시지 ---
# API 서버가 Tavily로 추출한 공고 원문을 S3에 업로드해두고 file_asset_id로 전달한다.
# 최상위 id는 post ID로, 콜백의 id로 에코백된다.
class PostAnalysisMessage(BaseJobMessage):
    file_asset_id: int
    job_type: JobType = JobType.POST_ANALYSIS


# --- Gemini structured output DTO ---
class PostAnalysisPayload(BaseModel):
    title: Annotated[str, Field(max_length=30)]
    summary: Annotated[str, Field(max_length=20)]
    company_intro: Annotated[str, Field(max_length=30)]

    rnr: Annotated[List[str], Field(max_length=5)]
    required_skills: Annotated[List[str], Field(max_length=5)]
    differentiators: Annotated[List[str], Field(max_length=3)]
    hidden_keywords: Annotated[List[str], Field(max_length=5)]
    action_items: Annotated[List[str], Field(max_length=3)]
