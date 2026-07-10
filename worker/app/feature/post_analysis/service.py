from typing import Any

from app.shared.client.file_store import S3FileStore
from app.shared.db.file_asset import SqlAlchemyFileAssetRepository
from app.feature.post_analysis.client import GeminiPostAnalyzer


# PostAnalysisService는 S3에 저장된 공고 원문을 내려받아 분석하는 비즈니스 로직을 담당합니다.
# API 서버가 Tavily로 추출한 공고 원문(rawContent)을 텍스트 파일로 업로드해두고,
# 그 file_asset_id를 메시지로 전달하면 워커가 S3에서 내려받아 Gemini로 분석합니다.
class PostAnalysisService:
    def __init__(
        self,
        post_analyzer: GeminiPostAnalyzer,
        file_store: S3FileStore,
        file_asset_repository: SqlAlchemyFileAssetRepository,
    ) -> None:
        self.post_analyzer = post_analyzer
        self.file_store = file_store
        self.file_asset_repository = file_asset_repository

    def process(self, file_asset_id: int) -> dict[str, Any]:
        print(f"log : post analysis file asset ID : {file_asset_id}")

        file_key = self.file_asset_repository.get_file_key(file_asset_id)
        file_bytes = self.file_store.download(file_key)

        post_content = file_bytes.decode("utf-8", errors="replace")

        return self.post_analyzer.analyze(post_content=post_content)
