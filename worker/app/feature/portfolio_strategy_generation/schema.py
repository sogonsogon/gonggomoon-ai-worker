from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.config.enums import JobType
from app.task.schema import BaseJobMessage


# --- 작업 메시지 (모든 데이터를 인라인으로 받음, DB 조회 없음) ---
class ExperienceInput(BaseModel):
    title: str = Field(description="경험 제목")
    experienceType: Literal["PROJECT", "CAREER", "EDUCATION", "COMPETITION", "OTHER"] = Field(
        description="경험 유형"
    )
    experienceContent: str = Field(description="경험 내용")
    teamSize: int = Field(description="팀 규모")
    startDate: Optional[str] = Field(default=None, description="시작일(ISO date), 예: 2024-03-15")
    endDate: Optional[str] = Field(default=None, description="종료일(ISO date), 예: 2024-09-30")
    roleType: Optional[str] = Field(default=None, description="역할 유형")
    impactTier: Optional[str] = Field(default=None, description="기여/임팩트 수준")


class PostAnalysisInput(BaseModel):
    title: str = Field(description="공고 분석 제목")
    summary: str = Field(description="공고 분석 요약")


class PortfolioStrategyGenerationMessage(BaseJobMessage):
    experiences: list[ExperienceInput]
    position_type: str
    industry_type: str
    # API 서버의 post_analysis 테이블 ID. 워커가 DB에서 title/summary를 조회해 프롬프트에 사용한다.
    post_analysis_id: int
    job_type: JobType = JobType.PORTFOLIO_STRATEGY_GENERATION


# --- Gemini structured output DTO ---
class ExperienceStrategyPoint(BaseModel):
    experienceType: Literal["PROJECT", "CAREER", "EDUCATION", "COMPETITION", "OTHER"] = Field(
        description="경험 유형"
    )
    experienceTitle: str = Field(description="경험 제목")
    strategyPoint: str = Field(description="해당 경험을 포트폴리오에서 어떻게 정리할지에 대한 전략 포인트")


class ExperienceOrderingItem(BaseModel):
    order: int = Field(description="포트폴리오 내 배치 순서", ge=1)
    title: str = Field(description="경험 제목")
    reason: str = Field(description="이 순서로 배치한 이유")


class ImprovementGuide(BaseModel):
    title: str = Field(description="개선 가이드 제목")
    description: str = Field(description="개선 가이드 설명")


class PortfolioStrategy(BaseModel):
    mainPositioningMessage: str = Field(
        description="사용자의 포지셔닝을 한 문장으로 요약한 메시지"
    )
    experienceStrategyPoints: list[ExperienceStrategyPoint] = Field(
        description="각 경험별 포트폴리오 전략 포인트"
    )
    experienceOrdering: list[ExperienceOrderingItem] = Field(
        description="포트폴리오에서 경험을 배치할 우선순위"
    )
    keywords: list[str] = Field(
        description="포트폴리오 전반에서 강조해야 할 핵심 키워드"
    )
    strengths: list[str] = Field(
        description="사용자의 강점을 요약한 리스트"
    )
    kpiCheckList: list[str] = Field(
        description="성과를 수치화할 때 확인해야 할 체크리스트"
    )
    improvementGuides: list[ImprovementGuide] = Field(
        description="포트폴리오 개선 가이드"
    )


class GeneratedPortfolioStrategyPayload(BaseModel):
    portfolioStrategy: PortfolioStrategy
