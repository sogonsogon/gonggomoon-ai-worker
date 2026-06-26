from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

# 로컬 개발 편의를 위해 .env가 있으면 로드한다.
# 배포 환경(Cloud Run 등)에는 .env 파일이 없고 환경변수가 직접 주입되므로,
# 파일 존재 여부가 아니라 "필수 환경변수 값"의 존재 여부로 검증한다.
load_dotenv()

# 반드시 환경변수로 주입되어야 하는 시크릿/인프라 설정 (기본값 없음)
REQUIRED_ENV_VARS = [
    "INTERNAL_API_KEY",
    "DATABASE_URL",
    "S3_BUCKET",
    "S3_ENDPOINT_URL",
    "S3_ACCESS_KEY",
    "S3_SECRET_KEY",
    "GEMINI_API_KEY",
]


@dataclass(frozen=True)
class Settings:
    # --- 필수 (시크릿/인프라) ---
    internal_api_key: str
    database_url: str
    s3_bucket: str
    s3_endpoint_url: str
    s3_access_key: str
    s3_secret_key: str
    gemini_api_key: str
    # --- 선택 (비밀이 아닌 운영 값, 기본값 허용) ---
    service_name: str = "ai-server"
    service_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8080
    s3_region: str | None = None
    gemini_model: str = "gemini-2.5-flash"


def get_settings() -> Settings:
    missing = [name for name in REQUIRED_ENV_VARS if not getenv(name)]
    if missing:
        raise RuntimeError(
            "필수 환경변수가 설정되어 있지 않습니다: "
            + ", ".join(missing)
            + " (.env 또는 배포 환경 변수를 확인하세요.)"
        )

    return Settings(
        internal_api_key=getenv("INTERNAL_API_KEY"),
        database_url=getenv("DATABASE_URL"),
        s3_bucket=getenv("S3_BUCKET"),
        s3_endpoint_url=getenv("S3_ENDPOINT_URL"),
        s3_access_key=getenv("S3_ACCESS_KEY"),
        s3_secret_key=getenv("S3_SECRET_KEY"),
        gemini_api_key=getenv("GEMINI_API_KEY"),
        service_name=getenv("SERVICE_NAME", "ai-server"),
        service_version=getenv("SERVICE_VERSION", "0.1.0"),
        host=getenv("HOST", "0.0.0.0"),
        port=int(getenv("PORT", "8080")),
        s3_region=getenv("S3_REGION"),
        gemini_model=getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    )
