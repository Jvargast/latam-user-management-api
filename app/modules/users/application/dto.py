from dataclasses import dataclass

from app.modules.users.domain.enums import UserRole


# DTOs usados para cruzar datos desde presentación hacia aplicación.
@dataclass(frozen=True, slots=True)
class CreateUserDTO:
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.USER
    active: bool = True


@dataclass(frozen=True, slots=True)
class UpdateUserDTO:
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole | None = None
    active: bool | None = None
