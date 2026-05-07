from enum import StrEnum

# Tipos de roles de user, mejor usar un enum y se evitan errores de string
class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
