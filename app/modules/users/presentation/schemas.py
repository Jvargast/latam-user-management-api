from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
)

from app.modules.users.domain.enums import UserRole


def normalize_email(value: EmailStr) -> str:
    # El email queda en minúsculas antes de llegar a aplicación (evitar duplicidad)
    return str(value).lower()


def reject_null_patch_value(value: object) -> object:
    # PATCH permite omitir campos, pero no enviarlos como null
    if value is None:
        raise ValueError("Field cannot be null")

    return value


# Tipos reutilizables para mantener consistentes las solicitudes
Username = Annotated[
    str,
    Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$"),
]
PersonName = Annotated[str, Field(min_length=1, max_length=100)]
NormalizedEmail = Annotated[EmailStr, AfterValidator(normalize_email)]
PatchUsername = Annotated[Username | None, BeforeValidator(reject_null_patch_value)]
PatchEmail = Annotated[NormalizedEmail | None, BeforeValidator(reject_null_patch_value)]
PatchPersonName = Annotated[PersonName | None, BeforeValidator(reject_null_patch_value)]
PatchRole = Annotated[UserRole | None, BeforeValidator(reject_null_patch_value)]
PatchActive = Annotated[bool | None, BeforeValidator(reject_null_patch_value)]


class UserWriteRequest(BaseModel):
    username: Username
    email: NormalizedEmail
    first_name: PersonName
    last_name: PersonName
    role: UserRole
    active: bool

    model_config = ConfigDict(str_strip_whitespace=True)


class UserCreateRequest(UserWriteRequest):
    role: UserRole = UserRole.USER
    active: bool = True

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "username": "latam.user",
                "email": "latam.user@example.com",
                "first_name": "Latam",
                "last_name": "User",
                "role": "user",
                "active": True,
            }
        },
    )


class UserUpdateRequest(UserWriteRequest):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "username": "latam.admin",
                "email": "latam.admin@example.com",
                "first_name": "Latam",
                "last_name": "Admin",
                "role": "admin",
                "active": True,
            }
        },
    )

# Patch para solo algunos campos
class UserPatchRequest(BaseModel):
    username: PatchUsername = None
    email: PatchEmail = None
    first_name: PatchPersonName = None
    last_name: PatchPersonName = None
    role: PatchRole = None
    active: PatchActive = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "first_name": "Latam",
                "active": False,
            }
        },
    )

# Response del usuario con todos los campos
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDeleteResponse(BaseModel):
    detail: str
