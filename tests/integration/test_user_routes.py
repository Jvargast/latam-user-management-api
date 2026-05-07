from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.modules.users.presentation.providers import provide_user_repository


def test_create_user_returns_created_user(api_client, user_payload):
    user_payload["email"] = "JANE.DOE@EXAMPLE.COM"

    response = api_client.post("/api/v1/users", json=user_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "jane.doe"
    assert data["email"] == "jane.doe@example.com"
    assert data["role"] == "user"
    assert data["active"] is True
    assert data["created_at"]
    assert data["updated_at"]


def test_create_user_rejects_duplicate_username(
    api_client,
    user_repository,
    user_payload,
):
    user_repository.add_user(username="jane.doe", email="existing@example.com")
    user_payload["email"] = "other@example.com"

    response = api_client.post("/api/v1/users", json=user_payload)

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}


def test_create_user_rejects_invalid_email(api_client, user_payload):
    user_payload["email"] = "invalid-email"

    response = api_client.post("/api/v1/users", json=user_payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "Validation error"
    assert response.json()["errors"][0]["field"] == "email"


def test_list_users_returns_paginated_users(api_client, user_repository):
    user_repository.add_user(username="first.user", email="first@example.com")
    second_user = user_repository.add_user(
        username="second.user",
        email="second@example.com",
    )
    user_repository.add_user(username="third.user", email="third@example.com")

    response = api_client.get("/api/v1/users", params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == second_user.id
    assert data[0]["username"] == "second.user"


def test_list_users_rejects_invalid_pagination(api_client):
    response = api_client.get("/api/v1/users", params={"limit": 0})

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {
            "field": "query.limit",
            "message": "Input should be greater than or equal to 1",
            "code": "greater_than_equal",
        }
    ]


def test_get_user_returns_existing_user(api_client, user_repository):
    user = user_repository.add_user(username="jane.doe", email="jane@example.com")

    response = api_client.get(f"/api/v1/users/{user.id}")

    assert response.status_code == 200
    assert response.json()["id"] == user.id
    assert response.json()["username"] == "jane.doe"


def test_get_user_returns_not_found_for_missing_user(api_client):
    response = api_client.get("/api/v1/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_get_user_rejects_invalid_id(api_client):
    response = api_client.get("/api/v1/users/0")

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {
            "field": "path.user_id",
            "message": "Input should be greater than or equal to 1",
            "code": "greater_than_equal",
        }
    ]


def test_put_user_updates_all_mutable_fields(api_client, user_repository):
    user = user_repository.add_user(username="jane.doe", email="jane@example.com")
    payload = {
        "username": "jane.admin",
        "email": "jane.admin@example.com",
        "first_name": "Jane",
        "last_name": "Admin",
        "role": "admin",
        "active": False,
    }

    response = api_client.put(f"/api/v1/users/{user.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["username"] == "jane.admin"
    assert data["email"] == "jane.admin@example.com"
    assert data["last_name"] == "Admin"
    assert data["role"] == "admin"
    assert data["active"] is False


def test_put_user_requires_full_payload(api_client, user_repository):
    user = user_repository.add_user(username="jane.doe", email="jane@example.com")
    payload = {
        "username": "jane.admin",
        "email": "jane.admin@example.com",
        "first_name": "Jane",
        "last_name": "Admin",
    }

    response = api_client.put(f"/api/v1/users/{user.id}", json=payload)

    assert response.status_code == 422
    missing_fields = {error["field"] for error in response.json()["errors"]}
    assert missing_fields == {"role", "active"}


def test_patch_user_updates_only_provided_fields(api_client, user_repository):
    user = user_repository.add_user(
        username="jane.doe",
        email="jane@example.com",
        first_name="Jane",
        last_name="Doe",
        active=True,
    )

    response = api_client.patch(
        f"/api/v1/users/{user.id}",
        json={"first_name": "Janet", "active": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "jane.doe"
    assert data["email"] == "jane@example.com"
    assert data["first_name"] == "Janet"
    assert data["last_name"] == "Doe"
    assert data["active"] is False


def test_patch_user_normalizes_email(api_client, user_repository):
    user = user_repository.add_user(username="jane.doe", email="jane@example.com")

    response = api_client.patch(
        f"/api/v1/users/{user.id}",
        json={"email": "JANE.UPDATED@EXAMPLE.COM"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "jane.updated@example.com"


def test_patch_user_rejects_empty_body(api_client, user_repository):
    user = user_repository.add_user(username="jane.doe", email="jane@example.com")

    response = api_client.patch(f"/api/v1/users/{user.id}", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "At least one field must be provided"}


def test_patch_user_rejects_null_fields(api_client, user_repository):
    user = user_repository.add_user(username="jane.doe", email="jane@example.com")

    response = api_client.patch(f"/api/v1/users/{user.id}", json={"active": None})

    assert response.status_code == 422
    assert response.json()["detail"] == "Validation error"
    assert response.json()["errors"][0]["field"] == "active"
    assert response.json()["errors"][0]["message"] == "Value error, Field cannot be null"


def test_patch_user_rejects_duplicate_email(api_client, user_repository):
    user_repository.add_user(username="jane.doe", email="jane@example.com")
    other_user = user_repository.add_user(
        username="other.user",
        email="other@example.com",
    )

    response = api_client.patch(
        f"/api/v1/users/{other_user.id}",
        json={"email": "jane@example.com"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already exists"}


def test_delete_user_removes_existing_user(api_client, user_repository):
    user = user_repository.add_user(username="jane.doe", email="jane@example.com")

    response = api_client.delete(f"/api/v1/users/{user.id}")

    assert response.status_code == 200
    assert response.json() == {"detail": "User deleted successfully"}
    assert user_repository.get_by_id(user.id) is None


def test_delete_user_returns_not_found_for_missing_user(api_client):
    response = api_client.delete("/api/v1/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_database_errors_return_service_unavailable():
    class FailingRepository:
        def list_users(self, limit, offset):
            raise SQLAlchemyError("database is unavailable")

    app.dependency_overrides[provide_user_repository] = lambda: FailingRepository()

    with TestClient(app) as client:
        response = client.get("/api/v1/users")

    app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"detail": "Database service unavailable"}
