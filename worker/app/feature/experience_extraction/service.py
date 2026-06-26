from typing import Any

from app.shared.client.file_store import S3FileStore
from app.shared.client.pdf_text_extractor import PyMuPdfTextExtractor
from app.shared.db.file_asset import SqlAlchemyFileAssetRepository
from app.shared.policy import validate_pdf_bytes
from app.feature.experience_extraction.client import GeminiExperienceAnalyzer

# ExperienceExtractionService는 PDF 파일에서 경험을 추출하는 핵심 비즈니스 로직을 담당합니다.
class ExperienceExtractionService:
    def __init__(
        self,
        file_store: S3FileStore,
        text_extractor: PyMuPdfTextExtractor,
        analyzer: GeminiExperienceAnalyzer,
        file_asset_repository: SqlAlchemyFileAssetRepository
    ) -> None:
        self.file_store = file_store
        self.text_extractor = text_extractor
        self.analyzer = analyzer
        self.file_asset_repository = file_asset_repository

    def process(self, file_asset_ids: list[dict[str, int]]) -> list[dict[str, Any]]:
        results = []

        for file_asset_id in file_asset_ids:
            file_key = self.file_asset_repository.get_file_key(file_asset_id["file_asset_id"])

            pdf_bytes = self.file_store.download(file_key)
            validate_pdf_bytes(pdf_bytes)

            resume_text = self.text_extractor.extract_text(pdf_bytes)

            result = self.analyzer.analyze(resume_text)
            results.append({
                "extracted_experience_id": file_asset_id["extracted_experience_id"],
                "file_asset_id": file_asset_id["file_asset_id"],
                "result": result,
            })

        return results
