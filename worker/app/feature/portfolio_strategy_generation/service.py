from typing import Any
from app.feature.portfolio_strategy_generation.client import GeminiPortfolioStrategyGenerator
from app.feature.portfolio_strategy_generation.schema import PortfolioStrategyGenerationMessage

class PortfolioStrategyService:
    def __init__(
        self,
        generator: GeminiPortfolioStrategyGenerator
    ):
        self.generator = generator

    def process(self, message: PortfolioStrategyGenerationMessage) -> dict[str, Any]:

        experiences = message.experiences
        position_type = message.position_type
        industry_type = message.industry_type
        post_analysis = message.post_analysis

        # 공고 분석 결과와 경험을 기반으로 포트폴리오 전략을 생성 (DB 조회 없이 메시지 인라인 데이터 사용)
        strategy_result = self.generator.generate(
            experiences=experiences,
            position_type=position_type,
            industry_type=industry_type,
            post_analysis=post_analysis
        )

        return strategy_result
