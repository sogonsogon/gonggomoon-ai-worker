from app.config.config import get_settings
from app.shared.db.session import create_session_factory
from app.shared.db.file_asset import SqlAlchemyFileAssetRepository
from app.shared.client.file_store import S3FileStore
from app.shared.client.callback_client import HttpCallbackClient
from app.shared.client.pdf_text_extractor import PyMuPdfTextExtractor
from app.feature.experience_extraction.client import GeminiExperienceAnalyzer
from app.feature.experience_extraction.service import ExperienceExtractionService
from app.feature.portfolio_strategy_generation.client import GeminiPortfolioStrategyGenerator
from app.feature.portfolio_strategy_generation.service import PortfolioStrategyService
from app.feature.interview_strategy_generation.client import GeminiInterviewStrategyGenerator
from app.feature.interview_strategy_generation.repository import SqlAlchemyInterviewStrategyRepository
from app.feature.interview_strategy_generation.service import InterviewStrategyService
from app.feature.post_analysis.client import GeminiPostAnalyzer
from app.feature.post_analysis.repository import SqlAlchemyPostRepository, SqlAlchemyCompanyRepository
from app.feature.post_analysis.service import PostAnalysisService
from app.task.dispatcher import Dispatcher
from app.task.executor import TaskExecutor

settings = get_settings()
session_factory = create_session_factory(settings.database_url)

# S3 호환 파일 스토어 클라이언트 (Supabase Storage)
file_store = S3FileStore(
    bucket=settings.s3_bucket,
    endpoint_url=settings.s3_endpoint_url,
    access_key=settings.s3_access_key,
    secret_key=settings.s3_secret_key,
    region=settings.s3_region,
)

# --- repositories ---
file_asset_repository = SqlAlchemyFileAssetRepository(session_factory=session_factory)
interview_strategy_repository = SqlAlchemyInterviewStrategyRepository(session_factory=session_factory)
company_repository = SqlAlchemyCompanyRepository(session_factory=session_factory)
post_repository = SqlAlchemyPostRepository(session_factory=session_factory)

text_extractor = PyMuPdfTextExtractor()

# --- gemini clients ---
experience_analyzer = GeminiExperienceAnalyzer(
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
)

portfolio_generator = GeminiPortfolioStrategyGenerator(
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
)

interview_generator = GeminiInterviewStrategyGenerator(
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
)

post_analyzer = GeminiPostAnalyzer(
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
)

# --- feature services ---
# 경험 추출 (pdf에서 경험을 추출하는 핵심 비즈니스 로직 담당)
experience_service = ExperienceExtractionService(
    file_store=file_store,
    analyzer=experience_analyzer,
    text_extractor=text_extractor,
    file_asset_repository=file_asset_repository
)

# 포트폴리오 전략 생성
portfolio_strategy_service = PortfolioStrategyService(
    generator=portfolio_generator
)

# 면접 전략 생성
interview_strategy_service = InterviewStrategyService(
    file_storage=file_store,
    text_extractor=text_extractor,
    file_asset_repository=file_asset_repository,
    interview_strategy_repository=interview_strategy_repository,
    generator=interview_generator
)

# 공고 분석
post_analysis_service = PostAnalysisService(
    post_analyzer=post_analyzer,
    company_repository=company_repository,
    post_repository=post_repository,
)

callback_client = HttpCallbackClient()

dispatcher = Dispatcher(
    experience_service=experience_service,
    portfolio_strategy_service=portfolio_strategy_service,
    interview_strategy_service=interview_strategy_service,
    post_analysis_service=post_analysis_service
)

task_executor = TaskExecutor(
    handler=dispatcher,
    callback_client=callback_client,
)
