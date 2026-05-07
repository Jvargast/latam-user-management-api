# Errores de las reglas de negocio
class UserDomainError(Exception):
    default_message = "User domain error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class UserNotFoundError(UserDomainError):
    default_message = "User not found"


class UserAlreadyExistsError(UserDomainError):
    default_message = "Username or email already exists"


class UsernameAlreadyExistsError(UserAlreadyExistsError):
    default_message = "Username already exists"


class EmailAlreadyExistsError(UserAlreadyExistsError):
    default_message = "Email already exists"
