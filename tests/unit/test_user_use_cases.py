import pytest

from app.modules.users.application.dto import CreateUserDTO, UpdateUserDTO
from app.modules.users.application.exceptions import EmptyUserUpdateError
from app.modules.users.application.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from app.modules.users.domain.enums import UserRole
from app.modules.users.domain.exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
)


def test_create_user_persists_user_with_defaults(user_repository):
    dto = CreateUserDTO(
        username="jane.doe",
        email="jane.doe@example.com",
        first_name="Jane",
        last_name="Doe",
    )

    user = CreateUserUseCase(user_repository).execute(dto)

    assert user.id == 1
    assert user.username == "jane.doe"
    assert user.email == "jane.doe@example.com"
    assert user.role == UserRole.USER
    assert user.active is True


def test_create_user_rejects_duplicate_username(user_repository):
    user_repository.add_user(username="jane.doe", email="jane@example.com")
    dto = CreateUserDTO(
        username="jane.doe",
        email="other@example.com",
        first_name="Other",
        last_name="User",
    )

    with pytest.raises(UsernameAlreadyExistsError):
        CreateUserUseCase(user_repository).execute(dto)


def test_create_user_rejects_duplicate_email(user_repository):
    user_repository.add_user(username="jane.doe", email="jane@example.com")
    dto = CreateUserDTO(
        username="other.user",
        email="jane@example.com",
        first_name="Other",
        last_name="User",
    )

    with pytest.raises(EmailAlreadyExistsError):
        CreateUserUseCase(user_repository).execute(dto)


def test_get_user_returns_existing_user(user_repository):
    existing_user = user_repository.add_user(
        username="jane.doe",
        email="jane@example.com",
    )

    user = GetUserUseCase(user_repository).execute(existing_user.id)

    assert user == existing_user


def test_get_user_raises_when_user_does_not_exist(user_repository):
    with pytest.raises(UserNotFoundError):
        GetUserUseCase(user_repository).execute(999)


def test_list_users_applies_limit_and_offset(user_repository):
    user_repository.add_user(username="first.user", email="first@example.com")
    second_user = user_repository.add_user(
        username="second.user",
        email="second@example.com",
    )
    user_repository.add_user(username="third.user", email="third@example.com")

    users = ListUsersUseCase(user_repository).execute(limit=1, offset=1)

    assert users == [second_user]


def test_update_user_updates_only_provided_fields(user_repository):
    existing_user = user_repository.add_user(
        username="jane.doe",
        email="jane@example.com",
        first_name="Jane",
        last_name="Doe",
        active=True,
    )

    updated_user = UpdateUserUseCase(user_repository).execute(
        existing_user.id,
        UpdateUserDTO(first_name="Janet", active=False),
    )

    assert updated_user.id == existing_user.id
    assert updated_user.username == "jane.doe"
    assert updated_user.email == "jane@example.com"
    assert updated_user.first_name == "Janet"
    assert updated_user.last_name == "Doe"
    assert updated_user.active is False


def test_update_user_accepts_current_username_and_email(user_repository):
    existing_user = user_repository.add_user(
        username="jane.doe",
        email="jane@example.com",
    )

    updated_user = UpdateUserUseCase(user_repository).execute(
        existing_user.id,
        UpdateUserDTO(username="jane.doe", email="jane@example.com"),
    )

    assert updated_user.username == existing_user.username
    assert updated_user.email == existing_user.email


def test_update_user_rejects_duplicate_username(user_repository):
    user_repository.add_user(username="jane.doe", email="jane@example.com")
    other_user = user_repository.add_user(
        username="other.user",
        email="other@example.com",
    )

    with pytest.raises(UsernameAlreadyExistsError):
        UpdateUserUseCase(user_repository).execute(
            other_user.id,
            UpdateUserDTO(username="jane.doe"),
        )


def test_update_user_rejects_duplicate_email(user_repository):
    user_repository.add_user(username="jane.doe", email="jane@example.com")
    other_user = user_repository.add_user(
        username="other.user",
        email="other@example.com",
    )

    with pytest.raises(EmailAlreadyExistsError):
        UpdateUserUseCase(user_repository).execute(
            other_user.id,
            UpdateUserDTO(email="jane@example.com"),
        )


def test_update_user_rejects_empty_update(user_repository):
    existing_user = user_repository.add_user(
        username="jane.doe",
        email="jane@example.com",
    )

    with pytest.raises(EmptyUserUpdateError):
        UpdateUserUseCase(user_repository).execute(existing_user.id, UpdateUserDTO())


def test_update_user_raises_when_user_does_not_exist(user_repository):
    with pytest.raises(UserNotFoundError):
        UpdateUserUseCase(user_repository).execute(
            999,
            UpdateUserDTO(first_name="Jane"),
        )


def test_delete_user_removes_existing_user(user_repository):
    existing_user = user_repository.add_user(
        username="jane.doe",
        email="jane@example.com",
    )

    DeleteUserUseCase(user_repository).execute(existing_user.id)

    assert user_repository.get_by_id(existing_user.id) is None


def test_delete_user_raises_when_user_does_not_exist(user_repository):
    with pytest.raises(UserNotFoundError):
        DeleteUserUseCase(user_repository).execute(999)
