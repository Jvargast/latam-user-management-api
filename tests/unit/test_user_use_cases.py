import pytest

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
from tests.helpers import assert_user_has, make_create_dto, make_update_dto


def test_create_user_persists_user_with_defaults(user_repository):
    # Se prueba la regla de aplicación sin pasar por HTTP ni validadores externos.
    user = CreateUserUseCase(user_repository).execute(make_create_dto())

    assert_user_has(
        user,
        id=1,
        username="latam.user",
        email="latam.user@example.com",
        role=UserRole.USER,
        active=True,
    )


# Se prueba la unicidad de username y email, regla clave del dominio.
@pytest.mark.parametrize(
    ("existing_user", "dto_changes", "expected_error"),
    [
        (
            {"username": "latam.user", "email": "latam@example.com"},
            {"email": "other@example.com"},
            UsernameAlreadyExistsError,
        ),
        (
            {"username": "existing.user", "email": "latam.user@example.com"},
            {"username": "other.user"},
            EmailAlreadyExistsError,
        ),
    ],
    ids=["username", "email"],
)
def test_create_user_rejects_duplicate_unique_fields(
    user_repository,
    existing_user,
    dto_changes,
    expected_error,
):
    user_repository.add_user(**existing_user)

    with pytest.raises(expected_error):
        CreateUserUseCase(user_repository).execute(make_create_dto(**dto_changes))


def test_get_user_returns_existing_user(user_repository):
    existing_user = user_repository.add_user(
        username="latam.user",
        email="latam@example.com",
    )

    user = GetUserUseCase(user_repository).execute(existing_user.id)

    assert user == existing_user


def test_get_user_raises_when_user_is_missing(user_repository):
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
        username="latam.user",
        email="latam@example.com",
        first_name="Latam",
        last_name="User",
        active=True,
    )

    updated_user = UpdateUserUseCase(user_repository).execute(
        existing_user.id,
        make_update_dto(first_name="Example", active=False),
    )

    assert_user_has(
        updated_user,
        id=existing_user.id,
        username="latam.user",
        email="latam@example.com",
        first_name="Example",
        last_name="User",
        active=False,
    )


def test_update_user_accepts_current_username_and_email(user_repository):
    existing_user = user_repository.add_user(
        username="latam.user",
        email="latam@example.com",
    )

    updated_user = UpdateUserUseCase(user_repository).execute(
        existing_user.id,
        make_update_dto(username="latam.user", email="latam@example.com"),
    )

    assert_user_has(
        updated_user,
        username=existing_user.username,
        email=existing_user.email,
    )


@pytest.mark.parametrize(
    ("dto_changes", "expected_error"),
    [
        ({"username": "latam.user"}, UsernameAlreadyExistsError),
        ({"email": "latam@example.com"}, EmailAlreadyExistsError),
    ],
    ids=["username", "email"],
)
def test_update_user_rejects_duplicate_unique_fields(
    user_repository,
    dto_changes,
    expected_error,
):
    user_repository.add_user(username="latam.user", email="latam@example.com")
    other_user = user_repository.add_user(
        username="other.user",
        email="other@example.com",
    )

    with pytest.raises(expected_error):
        UpdateUserUseCase(user_repository).execute(
            other_user.id,
            make_update_dto(**dto_changes),
        )


def test_update_user_rejects_empty_update(user_repository):
    existing_user = user_repository.add_user(
        username="latam.user",
        email="latam@example.com",
    )

    with pytest.raises(EmptyUserUpdateError):
        UpdateUserUseCase(user_repository).execute(existing_user.id, make_update_dto())


def test_update_user_raises_when_user_is_missing(user_repository):
    with pytest.raises(UserNotFoundError):
        UpdateUserUseCase(user_repository).execute(
            999,
            make_update_dto(first_name="Latam"),
        )


def test_delete_user_removes_existing_user(user_repository):
    existing_user = user_repository.add_user(
        username="latam.user",
        email="latam@example.com",
    )

    DeleteUserUseCase(user_repository).execute(existing_user.id)

    assert user_repository.get_by_id(existing_user.id) is None


def test_delete_user_raises_when_user_is_missing(user_repository):
    with pytest.raises(UserNotFoundError):
        DeleteUserUseCase(user_repository).execute(999)
