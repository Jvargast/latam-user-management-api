from fastapi import status

from app.core.error_messages import (
    DATABASE_SERVICE_UNAVAILABLE_MESSAGE,
    VALIDATION_ERROR_MESSAGE,
)
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
def validation_error_doc(
    description: str,
    examples: dict[str, dict[str, object]],
) -> ResponseDoc:
    return {
        "model": ValidationErrorResponse,
        "description": description,
        "content": {
            "application/json": {
                "examples": examples,
            }
        },
    }


INVALID_USER_ID_EXAMPLE = {
    "summary": "Invalid user ID",
    "value": {
        "detail": VALIDATION_ERROR_MESSAGE,
        "errors": [
            {
                "field": "path.user_id",
                "message": "Input should be greater than or equal to 1",
                "code": "greater_than_equal",
            }
        ],
    },
}
INVALID_EMAIL_EXAMPLE = {
    "summary": "Invalid email",
    "value": {
        "detail": VALIDATION_ERROR_MESSAGE,
        "errors": [
            {
                "field": "email",
                "message": "value is not a valid email address",
                "code": "value_error",
            }
        ],
    },
}
CREATE_VALIDATION_ERROR_RESPONSE = validation_error_doc(
    "Invalid user payload",
    {"invalid_email": INVALID_EMAIL_EXAMPLE},
)
LIST_VALIDATION_ERROR_RESPONSE = validation_error_doc(
    "Invalid pagination parameters",
    {
        "invalid_limit": {
            "summary": "Invalid limit",
            "value": {
                "detail": VALIDATION_ERROR_MESSAGE,
                "errors": [
                    {
                        "field": "query.limit",
                        "message": "Input should be greater than or equal to 1",
                        "code": "greater_than_equal",
                    }
                ],
            },
        }
    },
)
USER_ID_VALIDATION_ERROR_RESPONSE = validation_error_doc(
    "Invalid user ID",
    {"invalid_user_id": INVALID_USER_ID_EXAMPLE},
)
UPDATE_VALIDATION_ERROR_RESPONSE = validation_error_doc(
    "Invalid user ID or update payload",
    {
        "invalid_user_id": INVALID_USER_ID_EXAMPLE,
        "missing_field": {
            "summary": "Missing required field",
            "value": {
                "detail": VALIDATION_ERROR_MESSAGE,
                "errors": [
                    {
                        "field": "email",
                        "message": "Field required",
                        "code": "missing",
                    }
                ],
            },
        },
    },
)
PATCH_VALIDATION_ERROR_RESPONSE = validation_error_doc(
    "Invalid user ID or patch payload",
    {
        "invalid_user_id": INVALID_USER_ID_EXAMPLE,
        "null_field": {
            "summary": "Null field",
            "value": {
                "detail": VALIDATION_ERROR_MESSAGE,
                "errors": [
                    {
                        "field": "active",
                        "message": "Value error, Field cannot be null",
                        "code": "value_error",
                    }
                ],
            },
        },
    },
)
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
    status.HTTP_422_UNPROCESSABLE_CONTENT: CREATE_VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
LIST_USERS_RESPONSES: EndpointResponses = {
    status.HTTP_422_UNPROCESSABLE_CONTENT: LIST_VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
GET_USER_RESPONSES: EndpointResponses = {
    status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: USER_ID_VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
UPDATE_USER_RESPONSES: EndpointResponses = {
    status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
    status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: UPDATE_VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
PATCH_USER_RESPONSES: EndpointResponses = {
    status.HTTP_400_BAD_REQUEST: EMPTY_UPDATE_RESPONSE,
    status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
    status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: PATCH_VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
DELETE_USER_RESPONSES: EndpointResponses = {
    status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
    status.HTTP_422_UNPROCESSABLE_CONTENT: USER_ID_VALIDATION_ERROR_RESPONSE,
    status.HTTP_503_SERVICE_UNAVAILABLE: DATABASE_ERROR_RESPONSE,
}
