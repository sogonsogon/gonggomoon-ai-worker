from datetime import datetime, timezone
from typing import Any
from typing import Union

from app.config.enums import JobStatus, JobType
from app.task.schema import BaseJobMessage
from app.feature.experience_extraction.schema import ExtractedExperienceMessage
from app.feature.experience_extraction.service import ExperienceExtractionService
from app.feature.portfolio_strategy_generation.schema import PortfolioStrategyGenerationMessage
from app.feature.portfolio_strategy_generation.service import PortfolioStrategyService
from app.feature.interview_strategy_generation.schema import InterviewStrategyGenerationMessage
from app.feature.interview_strategy_generation.service import InterviewStrategyService
from app.feature.post_analysis.schema import PostAnalysisMessage
from app.feature.post_analysis.service import PostAnalysisService

JobMessage = Union[
    BaseJobMessage,
    ExtractedExperienceMessage,
    PortfolioStrategyGenerationMessage,
    InterviewStrategyGenerationMessage,
    PostAnalysisMessage
]

class Dispatcher:
    # TODO : feature가 늘어날 때 마다 추가해주자
    def __init__(self,
                 experience_service: ExperienceExtractionService,
                 portfolio_strategy_service: PortfolioStrategyService,
                 interview_strategy_service: InterviewStrategyService,
                 post_analysis_service: PostAnalysisService
                 ) -> None:
        self.experience_service = experience_service
        self.portfolio_strategy_service = portfolio_strategy_service
        self.interview_strategy_service = interview_strategy_service
        self.post_analysis_service = post_analysis_service

    # job_type에 따라 알맞은 feature service로 디스패치한다.
    def handle(self, message: JobMessage) -> dict[str, Any]:
        if message.job_type == JobType.EXPERIENCE_EXTRACTION:
            result = self.experience_service.process(message.file_asset_ids)
        elif message.job_type == JobType.PORTFOLIO_STRATEGY_GENERATION:
            result = self.portfolio_strategy_service.process(message)
        elif message.job_type == JobType.INTERVIEW_STRATEGY_GENERATION:
            result = self.interview_strategy_service.process(message)
        elif message.job_type == JobType.POST_ANALYSIS:
            result = self.post_analysis_service.process(message.file_asset_id)
        else:
            raise ValueError(f"Unsupported job type: {message.job_type}")

        print(f"Processed job {message.id} of type {message.job_type}. Result: {result}")
        return {
            "type": message.job_type.value,
            "id": message.id,
            "user_id": str(message.user_id),
            "status": JobStatus.COMPLETED.value,
            "result": result,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
