from typing import Any

from app.shared.client.file_store import S3FileStore
from app.shared.db.file_asset import SqlAlchemyFileAssetRepository
from app.shared.policy import resolve_document_mime_type, validate_pdf_bytes
from app.feature.experience_extraction.client import GeminiExperienceAnalyzer

# ExperienceExtractionService는 업로드된 문서에서 경험을 추출하는 핵심 비즈니스 로직을 담당합니다.
# 파일을 Gemini 멀티모달 입력으로 직접 전달하므로 텍스트 추출(OCR 포함) 단계가 필요하지 않습니다.
class ExperienceExtractionService:
    def __init__(
        self,
        file_store: S3FileStore,
        analyzer: GeminiExperienceAnalyzer,
        file_asset_repository: SqlAlchemyFileAssetRepository
    ) -> None:
        self.file_store = file_store
        self.analyzer = analyzer
        self.file_asset_repository = file_asset_repository

    def process(self, file_asset_ids: list[dict[str, int]]) -> list[dict[str, Any]]:
        results = []

        for file_asset_id in file_asset_ids:
            file_key = self.file_asset_repository.get_file_key(file_asset_id["file_asset_id"])

            file_bytes, content_type = self.file_store.download_with_content_type(file_key)
            validate_pdf_bytes(file_bytes)

            mime_type = resolve_document_mime_type(content_type, file_bytes)

            result = self.analyzer.analyze(file_bytes, mime_type)
            results.append({
                "extracted_experience_id": file_asset_id["extracted_experience_id"],
                "file_asset_id": file_asset_id["file_asset_id"],
                "result": result,
            })

        return results
