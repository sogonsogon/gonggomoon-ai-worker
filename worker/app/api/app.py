from fastapi import FastAPI

from app.api.router import router
from app.core.config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.service_name,
        version=settings.service_version,
    )
    app.include_router(router)
    return app


app = create_app()
