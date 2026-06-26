from typing import Any

from app.shared.client.file_store import S3FileStore
from app.shared.client.pdf_text_extractor import PyMuPdfTextExtractor
from app.shared.db.file_asset import SqlAlchemyFileAssetRepository
from app.shared.policy import validate_pdf_bytes
from app.feature.interview_strategy_generation.client import GeminiInterviewStrategyGenerator
from app.feature.interview_strategy_generation.repository import SqlAlchemyInterviewStrategyRepository
from app.feature.interview_strategy_generation.schema import InterviewStrategyGenerationMessage


class InterviewStrategyService:
    def __init__(
            self,
            file_storage: S3FileStore,
            text_extractor: PyMuPdfTextExtractor,
            interview_strategy_repository: SqlAlchemyInterviewStrategyRepository,
            file_asset_repository: SqlAlchemyFileAssetRepository,
            generator: GeminiInterviewStrategyGenerator
        ):
        self.generator = generator
        self.file_storage = file_storage
        self.text_extractor = text_extractor
        self.file_asset_repository = file_asset_repository
        self.interview_strategy_repository = interview_strategy_repository

    def process(self, message: InterviewStrategyGenerationMessage) -> dict[str, Any]:
        # interview_strategy_repository에서 file_asset_id를 받아와야 함.
        file_asset_id = self.interview_strategy_repository.get_file_asset_id(message.id)

        # 여기서 file_asset_id로 DB에서 Key값을 조회해와야 함.
        file_key = self.file_asset_repository.get_file_key(file_asset_id)

        # S3에서 PDF를 다운로드 해온다.
        pdf_bytes = self.file_storage.download(file_key)
        validate_pdf_bytes(pdf_bytes)

        # PDF에서 텍스트를 추출한다.
        resume_text = self.text_extractor.extract_text(pdf_bytes)

        # generator를 호출하여 면접 전략을 생성
        strategy_result = self.generator.generate(
            resume_text=resume_text
        )

        return strategy_result
