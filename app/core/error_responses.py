from pydantic import BaseModel, ConfigDict, Field

from app.core.error_messages import VALIDATION_ERROR_MESSAGE


# Borde HTTP, fuera de dominio y aplicación
# La API expone JSON estable aunque el error sea en capas internas
class ErrorResponse(BaseModel):
    detail: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Error detail",
            }
        }
    )


class ValidationErrorDetail(BaseModel):
    field: str
    message: str
    code: str


class ValidationErrorResponse(BaseModel):
    detail: str = Field(examples=[VALIDATION_ERROR_MESSAGE])
    errors: list[ValidationErrorDetail]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": VALIDATION_ERROR_MESSAGE,
                "errors": [
                    {
                        "field": "field",
                        "message": "Invalid value",
                        "code": "validation_error",
                    }
                ],
            }
        }
    )


# Función para crear respuesta de error con formato
def error_response_doc(description: str, detail: str) -> dict[str, object]:
    return {
        "model": ErrorResponse,
        "description": description,
        "content": {
            "application/json": {
                "example": {
                    "detail": detail,
                }
            }
        },
    }
