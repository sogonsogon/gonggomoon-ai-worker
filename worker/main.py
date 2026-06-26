import uvicorn

from app.config.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.presentation.app:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
