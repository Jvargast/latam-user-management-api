from dataclasses import asdict, replace
from typing import TypeAlias, cast

from app.modules.users.application.dto import CreateUserDTO, UpdateUserDTO
from app.modules.users.application.exceptions import EmptyUserUpdateError
from app.modules.users.domain.entities import User
from app.modules.users.domain.enums import UserRole
from app.modules.users.domain.exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
)
from app.modules.users.domain.ports import UserRepository

UserValue: TypeAlias = str | bool | UserRole
UserUpdateValues: TypeAlias = dict[str, UserValue]


class CreateUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def execute(self, dto: CreateUserDTO) -> User:
        # Se revisa unicidad para evitar duplicados
        self._ensure_username_is_available(dto.username)
        self._ensure_email_is_available(dto.email)

        return self.repository.create(
            User(
                id=None,
                username=dto.username,
                email=dto.email,
                first_name=dto.first_name,
                last_name=dto.last_name,
                role=dto.role,
                active=dto.active,
            )
        )

    def _ensure_username_is_available(self, username: str) -> None:
        if self.repository.get_by_username(username) is not None:
            raise UsernameAlreadyExistsError()

    def _ensure_email_is_available(self, email: str) -> None:
        if self.repository.get_by_email(email) is not None:
            raise EmailAlreadyExistsError()


class GetUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def execute(self, user_id: int) -> User:
        # Si no existe, el caso de uso corta el flujo con error de dominio
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        return user


class ListUsersUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def execute(self, limit: int, offset: int) -> list[User]:
        # La paginación vive en el repositorio y este caso de uso queda liviano
        return self.repository.list_users(limit=limit, offset=offset)


class UpdateUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def execute(self, user_id: int, dto: UpdateUserDTO) -> User:
        # PUT y PATCH comparten flujo, cambian los campos recibidos
        current_user = self._get_user_or_raise(user_id)
        values = self._get_update_values(dto)

        self._ensure_unique_fields_are_available(
            values=values,
            current_user_id=user_id,
        )
        # Una vez validados los campos, se crea nueva entidad
        updated_user = replace(current_user, **values)

        return self.repository.update(updated_user)

    def _get_user_or_raise(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        return user

    @staticmethod
    def _get_update_values(dto: UpdateUserDTO) -> UserUpdateValues:
        # Campos vacíos quedan fuera y no hay escrituras sin intención
        values = {
            field_name: value
            for field_name, value in asdict(dto).items()
            if value is not None
        }

        if not values:
            raise EmptyUserUpdateError()

        return cast(UserUpdateValues, values)

    def _ensure_unique_fields_are_available(
        self,
        *,
        values: UserUpdateValues,
        current_user_id: int,
    ) -> None:
        # El mismo username o email es válido si pertenece al usuario actual
        username = cast(str | None, values.get("username"))
        email = cast(str | None, values.get("email"))

        if username is not None:
            existing_user = self.repository.get_by_username(username)

            if existing_user is not None and existing_user.id != current_user_id:
                raise UsernameAlreadyExistsError()

        if email is not None:
            existing_user = self.repository.get_by_email(email)

            if existing_user is not None and existing_user.id != current_user_id:
                raise EmailAlreadyExistsError()


class DeleteUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def execute(self, user_id: int) -> None:
        # La existencia previa define si corresponde responder 404
        if self.repository.get_by_id(user_id) is None:
            raise UserNotFoundError()

        self.repository.delete(user_id)
