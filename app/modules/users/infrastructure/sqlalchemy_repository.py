from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.users.domain.entities import User
from app.modules.users.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.modules.users.infrastructure.mappers import entity_to_model, model_to_entity
from app.modules.users.infrastructure.sqlalchemy_model import UserModel


class SQLAlchemyUserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user: User) -> User:
        # La entidad de dominio pasa a registro SQLAlchemy en este borde
        model = entity_to_model(user)

        try:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return model_to_entity(model)

        except IntegrityError as error:
            # Evita duplicados por email o username
            self.db.rollback()
            raise UserAlreadyExistsError("Username or email already exists") from error

    def get_by_id(self, user_id: int) -> User | None:
        # El modelo vuelve a entidad antes de salir de infraestructura
        model = self.db.get(UserModel, user_id)
        return model_to_entity(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        statement = select(UserModel).where(UserModel.email == email)
        model = self.db.scalar(statement)
        return model_to_entity(model) if model else None

    def get_by_username(self, username: str) -> User | None:
        statement = select(UserModel).where(UserModel.username == username)
        model = self.db.scalar(statement)
        return model_to_entity(model) if model else None

    def list_users(self, limit: int, offset: int) -> list[User]:
        # Se ordena por id para la paginación sea consistente
        statement = select(UserModel).order_by(UserModel.id).limit(limit).offset(offset)

        models = self.db.scalars(statement).all()
        return [model_to_entity(model) for model in models]

    def update(self, user: User) -> User:
        # Se busca el usuario por id y se actualizan sus campos
        if user.id is None:
            raise ValueError("Cannot update a user without an id")

        model = self.db.get(UserModel, user.id)

        if model is None:
            raise UserNotFoundError()

        model.username = user.username
        model.email = user.email
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.role = user.role
        model.active = user.active

        try:
            self.db.commit()
            self.db.refresh(model)
            return model_to_entity(model)

        except IntegrityError as error:
            # La base confirma conflictos de username o email
            self.db.rollback()
            raise UserAlreadyExistsError("Username or email already exists") from error

    def delete(self, user_id: int) -> None:
        model = self.db.get(UserModel, user_id)

        if model is None:
            return

        self.db.delete(model)
        self.db.commit()
