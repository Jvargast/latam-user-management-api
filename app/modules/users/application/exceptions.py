# Errores del flujo de aplicación, separados de las reglas del dominio
class UserApplicationError(Exception):
    default_message = "User application error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class EmptyUserUpdateError(UserApplicationError):
    default_message = "At least one field must be provided"
