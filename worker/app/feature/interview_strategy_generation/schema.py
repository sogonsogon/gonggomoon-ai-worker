from enum import StrEnum
from pydantic import BaseModel, Field

from app.config.enums import JobType
from app.task.schema import BaseJobMessage


# --- 작업 메시지 ---
class InterviewStrategyGenerationMessage(BaseJobMessage):
    job_type: JobType = JobType.INTERVIEW_STRATEGY_GENERATION


# --- Gemini structured output DTO ---
class QuestionLevel(StrEnum):
    HIGH = "HIGH"
    MIDDLE = "MIDDLE"
    LOWER = "LOWER"


class InterviewQuestion(BaseModel):
    question: str = Field(description="면접 질문")
    questionLevel: QuestionLevel = Field(description="질문 난이도")


class GeneratedInterviewStrategyPayload(BaseModel):
    questions: list[InterviewQuestion]
