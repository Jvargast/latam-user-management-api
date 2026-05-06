from dataclasses import dataclass
from datetime import datetime

from app.modules.users.domain.enums import UserRole

@dataclass
class User:
    id: int | None
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
