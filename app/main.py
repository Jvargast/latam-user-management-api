import logging

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.error_messages import DATABASE_SERVICE_UNAVAILABLE_MESSAGE
from app.core.error_responses import error_response_doc
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.modules.users.presentation.routes import router as users_router
from app.shared.database.session import engine

# La configuración de registros queda lista antes de rutas y chequeos de salud.
configure_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.app_name,
    description="RESTful API for user management",
    version=settings.app_version,
)

# Los errores globales se registran una vez sobre la aplicación principal.
register_exception_handlers(app)

# El módulo de usuarios mantiene sus rutas agrupadas bajo su propio prefijo.
app.include_router(users_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    # Respuesta liviana para saber si la API está levantada.
    return {"status": "ok"}


@app.get(
    "/health/db",
    tags=["Health"],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: error_response_doc(
            DATABASE_SERVICE_UNAVAILABLE_MESSAGE,
            DATABASE_SERVICE_UNAVAILABLE_MESSAGE,
        )
    },
)
def database_health_check() -> dict[str, str]:
    try:
        # Este chequeo confirma que la conexión real a la base responde.
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Database health check completed successfully")

        return {"database": "ok"}

    except SQLAlchemyError as error:
        logger.exception("Database health check failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_SERVICE_UNAVAILABLE_MESSAGE,
        ) from error
