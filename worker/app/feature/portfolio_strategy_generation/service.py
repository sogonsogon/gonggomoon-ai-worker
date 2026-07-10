from typing import Any

from app.feature.portfolio_strategy_generation.client import GeminiPortfolioStrategyGenerator
from app.feature.portfolio_strategy_generation.repository import SqlAlchemyPostAnalysisRepository
from app.feature.portfolio_strategy_generation.schema import (
    PortfolioStrategyGenerationMessage,
    PostAnalysisInput,
)


class PortfolioStrategyService:
    def __init__(
        self,
        generator: GeminiPortfolioStrategyGenerator,
        post_analysis_repository: SqlAlchemyPostAnalysisRepository,
    ):
        self.generator = generator
        self.post_analysis_repository = post_analysis_repository

    def process(self, message: PortfolioStrategyGenerationMessage) -> dict[str, Any]:

        # API 서버가 전달한 post_analysis_id로 공고 분석 결과(title/summary)를 조회해 프롬프트에 사용한다.
        title, summary = self.post_analysis_repository.get_title_and_summary(message.post_analysis_id)
        post_analysis = PostAnalysisInput(title=title, summary=summary)

        strategy_result = self.generator.generate(
            experiences=message.experiences,
            position_type=message.position_type,
            industry_type=message.industry_type,
            post_analysis=post_analysis
        )

        return strategy_result
