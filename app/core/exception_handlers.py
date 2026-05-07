import logging
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.error_messages import (
    DATABASE_SERVICE_UNAVAILABLE_MESSAGE,
    HTTP_ERROR_MESSAGE,
    VALIDATION_ERROR_MESSAGE,
)
from app.core.error_responses import ErrorResponse, ValidationErrorResponse
from app.modules.users.application.exceptions import EmptyUserUpdateError
from app.modules.users.domain.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


def error_response(status_code: int, detail: str) -> JSONResponse:
    # Respuesta simple para errores controlados
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(detail=detail).model_dump(),
    )

# Handler para errror de usuario inexistente, repuesta 404
def user_not_found_handler(
    _request: Request,
    exc: UserNotFoundError,
) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, str(exc))

# Handler para error de usuario existente, respuesta 409
def user_already_exists_handler(
    _request: Request,
    exc: UserAlreadyExistsError,
) -> JSONResponse:
    return error_response(status.HTTP_409_CONFLICT, str(exc))

# Handler para error de actualización sin campos, un 400
def empty_user_update_handler(
    _request: Request,
    exc: EmptyUserUpdateError,
) -> JSONResponse:
    return error_response(status.HTTP_400_BAD_REQUEST, str(exc))

# Handler error http
def http_exception_handler(
    _request: Request,
    exc: HTTPException,
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else HTTP_ERROR_MESSAGE
    return error_response(exc.status_code, detail)


def request_validation_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    # Las validaciones salen limpias, sin datos internos de Pydantic
    response = ValidationErrorResponse(
        detail=VALIDATION_ERROR_MESSAGE,
        errors=[
            {
                "field": format_error_location(error.get("loc", ())),
                "message": str(error.get("msg", "Invalid value")),
                "code": str(error.get("type", "validation_error")),
            }
            for error in exc.errors()
        ],
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(),
    )


def format_error_location(location: Sequence[Any]) -> str:
    # Ubicación del error formateada
    parts = [str(part) for part in location if part != "body"]
    return ".".join(parts) if parts else "body"


def database_error_handler(
    _request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    # El registro con detalle real
    logger.error(
        "Database error while processing request",
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return error_response(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        DATABASE_SERVICE_UNAVAILABLE_MESSAGE,
    )


def register_exception_handlers(app: FastAPI) -> None:
    # Los handlers globales quedan listos antes de las rutas
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(SQLAlchemyError, database_error_handler)
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
    app.add_exception_handler(EmptyUserUpdateError, empty_user_update_handler)
