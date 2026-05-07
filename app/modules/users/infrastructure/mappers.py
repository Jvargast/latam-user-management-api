from app.modules.users.domain.entities import User
from app.modules.users.domain.enums import UserRole
from app.modules.users.infrastructure.sqlalchemy_model import UserModel


# Los modelos SQLAlchemy no cruzan hacia dominio ni aplicación
def model_to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        email=model.email,
        first_name=model.first_name,
        last_name=model.last_name,
        role=UserRole(model.role),
        active=model.active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def entity_to_model(user: User) -> UserModel:
    # La base asigna id y fechas al persistir el registro
    return UserModel(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        active=user.active,
    )
