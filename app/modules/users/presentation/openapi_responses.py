from fastapi import status

from app.core.error_messages import DATABASE_SERVICE_UNAVAILABLE_MESSAGE
from app.core.error_responses import (
    ErrorResponse,
    ValidationErrorResponse,
    error_response_doc,
)
from app.modules.users.application.exceptions import EmptyUserUpdateError
from app.modules.users.domain.exceptions import (
    EmailAlreadyExistsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
)

ResponseDoc = dict[str, object]
EndpointResponses = dict[int, ResponseDoc]


# Se anotan las posibles respuestas de error para cada endpoint de forma explícita
VALIDATION_ERROR_RESPONSE: ResponseDoc = {
    "model": ValidationErrorResponse,
    "description": "Request validation error",
}
NOT_FOUND_RESPONSE = error_response_doc(
    UserNotFoundError.default_message,
    UserNotFoundError.default_message,
)
CONFLICT_RESPONSE: ResponseDoc = {
    "model": ErrorResponse,
    "description": UserAlreadyExistsError.default_message,
    "content": {
        "application/json": {
            "examples": {
                "username": {
                    "summary": UsernameAlreadyExistsError.default_message,
                    "value": {"detail": UsernameAlreadyExistsError.default_message},
                },
                "email": {
                    "summary": EmailAlreadyExistsError.default_message,
                    "value": {"detail": EmailAlreadyExistsError.default_message},
                },
            }
        }
    },
}
EMPTY_UPDATE_RESPONSE = error_response_doc(
    "No update fields were provided",
    EmptyUserUpdateError.default_message,
)
DATABASE_ERROR_RESPONSE = error_response_doc(
    DATABASE_SERVICE_UNAVAILABLE_MESSAGE,
    DATABASE_SERVICE_UNAVAILABLE_MESSAGE,
)


CREATE_USER_RESPONSES: EndpointResponses = {
    status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
LIST_USERS_RESPONSES: EndpointResponses = {
    status.HTTP_422_UNPROCESSABLE_CONTENT: VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
GET_USER_RESPONSES: EndpointResponses = {
    status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
UPDATE_USER_RESPONSES: EndpointResponses = {
    status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
    status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
PATCH_USER_RESPONSES: EndpointResponses = {
    status.HTTP_400_BAD_REQUEST: EMPTY_UPDATE_RESPONSE,
    status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
    status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
DELETE_USER_RESPONSES: EndpointResponses = {
    status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
