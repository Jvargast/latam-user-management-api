from typing import Any

from httpx import Response

from app.modules.users.application.dto import CreateUserDTO, UpdateUserDTO
from app.modules.users.domain.entities import User

USERS_URL = "/api/v1/users"
USER_FIELDS = ("username", "email", "first_name", "last_name", "role", "active")


def make_create_dto(**overrides: Any) -> CreateUserDTO:
    values = {
        "username": "latam.user",
        "email": "latam.user@example.com",
        "first_name": "Latam",
        "last_name": "User",
    }
    values.update(overrides)
    return CreateUserDTO(**values)


def make_update_dto(**overrides: Any) -> UpdateUserDTO:
    return UpdateUserDTO(**overrides)


def make_update_payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "username": "latam.admin",
        "email": "latam.admin@example.com",
        "first_name": "Latam",
        "last_name": "Admin",
        "role": "admin",
        "active": False,
    }
    payload.update(overrides)
    return payload


def expected_from_user(user: User) -> dict[str, Any]:
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.value,
        "active": user.active,
    }


def assert_user_has(user: User, **expected: Any) -> None:
    for field, value in expected.items():
        assert getattr(user, field) == value


def assert_user_response(
    data: dict[str, Any],
    expected: dict[str, Any],
    *,
    user_id: int | None = None,
) -> None:
    if user_id is not None:
        assert data["id"] == user_id

    for field in USER_FIELDS:
        assert data[field] == expected[field]

    assert data["created_at"]
    assert data["updated_at"]


def assert_detail_response(response: Response, status_code: int, detail: str) -> None:
    assert response.status_code == status_code
    assert response.json() == {"detail": detail}


def assert_validation_error(response: Response, field: str) -> dict[str, Any]:
    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Validation error"

    matching_errors = [error for error in body["errors"] if error["field"] == field]
    assert matching_errors
    return matching_errors[0]
