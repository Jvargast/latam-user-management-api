from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.users.domain.ports import UserRepository
from app.modules.users.infrastructure.sqlalchemy_repository import (
    SQLAlchemyUserRepository,
)
from app.shared.database.session import get_db

DatabaseSession = Annotated[Session, Depends(get_db)]


# Este proveedor conecta FastAPI con el puerto de dominio
def provide_user_repository(db: DatabaseSession) -> UserRepository:
    return SQLAlchemyUserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(provide_user_repository)]
