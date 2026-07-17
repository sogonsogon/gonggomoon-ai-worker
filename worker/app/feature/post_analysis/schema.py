from typing import List
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
# 최대 길이/개수는 프롬프트로 유도하고, 배열이 비어 있지 않다는 조건만 스키마로 강제한다.
# 하드 제약(max_length)을 걸면 모델 출력이 조금만 벗어나도 작업 전체가 실패하므로 두지 않는다.
class PostAnalysisPayload(BaseModel):
    title: str
    summary: str
    company_intro: str

    rnr: List[str] = Field(min_length=1)
    required_skills: List[str] = Field(min_length=1)
    differentiators: List[str] = Field(min_length=1)
    hidden_keywords: List[str] = Field(min_length=1)
    action_items: List[str] = Field(min_length=1)
