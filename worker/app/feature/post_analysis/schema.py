from typing import List
from pydantic import BaseModel

from app.config.enums import JobType
from app.task.schema import BaseJobMessage


# --- 작업 메시지 ---
# API 서버가 Tavily로 추출한 공고 원문을 S3에 업로드해두고 file_asset_id로 전달한다.
# 최상위 id는 post ID로, 콜백의 id로 에코백된다.
class PostAnalysisMessage(BaseJobMessage):
    file_asset_id: int
    job_type: JobType = JobType.POST_ANALYSIS


# --- Gemini structured output DTO ---
# 길이/개수 가이드는 프롬프트로만 유도한다.
# 하드 제약(max_length)을 걸면 모델 출력이 조금만 벗어나도 작업 전체가 실패하므로 두지 않는다.
class PostAnalysisPayload(BaseModel):
    title: str
    summary: str
    company_intro: str

    rnr: List[str]
    required_skills: List[str]
    differentiators: List[str]
    hidden_keywords: List[str]
    action_items: List[str]
