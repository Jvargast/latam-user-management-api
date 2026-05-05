import logging

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import configure_logging
from app.shared.database.session import engine

configure_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.app_name,
    description="RESTful API for user management built with FastAPI and PostgreSQL.",
    version=settings.app_version,
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db", tags=["Health"])
def database_health_check() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    logger.info("Database health check completed successfully")

    return {"database": "ok"}
