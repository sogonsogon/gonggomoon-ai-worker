from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    service_name: str = "ai-server"
    service_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8080
    internal_api_key: str = "local-dev-secret"
    database_url: str | None = None
    s3_bucket: str | None = None
    s3_region: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"


def get_settings() -> Settings:
    return Settings(
        service_name=getenv("SERVICE_NAME", "ai-server"),
        service_version=getenv("SERVICE_VERSION", "0.1.0"),
        host=getenv("HOST", "0.0.0.0"),
        port=int(getenv("PORT", "8080")),
        internal_api_key=getenv("INTERNAL_API_KEY", "local-dev-secret"),
        database_url=getenv("DATABASE_URL"),
        s3_bucket=getenv("S3_BUCKET"),
        s3_region=getenv("AWS_REGION"),
        gemini_api_key=getenv("GEMINI_API_KEY"),
        gemini_model=getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    )
