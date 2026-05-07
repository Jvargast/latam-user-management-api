import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.modules.users.presentation.providers import provide_user_repository
from tests.helpers import (
    USERS_URL,
    assert_detail_response,
    assert_user_response,
    assert_validation_error,
    expected_from_user,
    make_update_payload,
)

def test_create_user_returns_created_user(api_client, user_payload):
    # Se prueba que POST crea el usuario y normaliza el email antes de responder
    payload = {**user_payload, "email": "LATAM.USER@EXAMPLE.COM"}

    response = api_client.post(USERS_URL, json=payload)

    assert response.status_code == 201
    assert_user_response(
        response.json(),
        {**payload, "email": "latam.user@example.com"},
        user_id=1,
    )


def test_create_user_rejects_duplicate_username(
    api_client,
    user_payload,
    existing_user,
):
    payload = {**user_payload, "email": "other@example.com"}

    response = api_client.post(USERS_URL, json=payload)

    assert existing_user.username == payload["username"]
    assert_detail_response(response, 409, "Username already exists")


def test_list_users_returns_requested_page(api_client, user_repository):
    user_repository.add_user(username="first.user", email="first@example.com")
    second_user = user_repository.add_user(
        username="second.user",
        email="second@example.com",
    )
    # El tercer usuario confirma que el offset realmente salta registros
    user_repository.add_user(username="third.user", email="third@example.com")

    response = api_client.get(USERS_URL, params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert_user_response(data[0], expected_from_user(second_user), user_id=second_user.id)


def test_get_user_returns_existing_user(api_client, existing_user):
    response = api_client.get(f"{USERS_URL}/{existing_user.id}")

    assert response.status_code == 200
    assert_user_response(
        response.json(),
        expected_from_user(existing_user),
        user_id=existing_user.id,
    )


def test_get_user_returns_not_found_for_missing_user(api_client):
    # Probando que el get de un usuario inexistente devuelva el error correcto
    response = api_client.get(f"{USERS_URL}/999")

    assert_detail_response(response, 404, "User not found")


def test_put_user_replaces_mutable_fields(api_client, existing_user):
    payload = make_update_payload()

    response = api_client.put(f"{USERS_URL}/{existing_user.id}", json=payload)

    assert response.status_code == 200
    assert_user_response(response.json(), payload, user_id=existing_user.id)


def test_put_user_requires_full_payload(api_client, existing_user):
    # Se requiere el payload completo para put
    payload = make_update_payload()
    payload.pop("role")
    payload.pop("active")

    response = api_client.put(f"{USERS_URL}/{existing_user.id}", json=payload)

    assert response.status_code == 422
    assert {error["field"] for error in response.json()["errors"]} == {"role", "active"}


def test_patch_user_updates_only_provided_fields(api_client, existing_user):
    response = api_client.patch(
        f"{USERS_URL}/{existing_user.id}",
        json={"first_name": "Example", "email": "LATAM.UPDATED@EXAMPLE.COM", "active": False},
    )

    expected = {
        **expected_from_user(existing_user),
        "first_name": "Example",
        "email": "latam.updated@example.com",
        "active": False,
    }
    assert response.status_code == 200
    assert_user_response(response.json(), expected, user_id=existing_user.id)

# Validación de unicidad, rechazar duplicados
def test_patch_user_rejects_duplicate_email(api_client, user_repository, existing_user):
    other_user = user_repository.add_user(
        username="other.user",
        email="other@example.com",
    )

    response = api_client.patch(
        f"{USERS_URL}/{other_user.id}",
        json={"email": existing_user.email},
    )

    assert_detail_response(response, 409, "Email already exists")


@pytest.mark.parametrize(
    ("payload", "field"),
    [({}, None), ({"active": None}, "active")],
    ids=["empty", "null"],
)
def test_patch_user_rejects_invalid_body(api_client, existing_user, payload, field):
    response = api_client.patch(f"{USERS_URL}/{existing_user.id}", json=payload)

    if field is None:
        assert_detail_response(response, 400, "At least one field must be provided")
        return

    error = assert_validation_error(response, field)
    assert error["message"] == "Value error, Field cannot be null"


def test_delete_user_removes_existing_user(api_client, user_repository, existing_user):
    response = api_client.delete(f"{USERS_URL}/{existing_user.id}")

    assert_detail_response(response, 200, "User deleted successfully")
    assert user_repository.get_by_id(existing_user.id) is None


@pytest.mark.parametrize(
    ("path", "params", "field"),
    [
        (USERS_URL, {"limit": 0}, "query.limit"),
        (f"{USERS_URL}/0", None, "path.user_id"),
    ],
    ids=["limit", "user_id"],
)
def test_route_parameters_are_validated(api_client, path, params, field):
    response = api_client.get(path, params=params)

    error = assert_validation_error(response, field)
    assert error["code"] == "greater_than_equal"


def test_create_user_rejects_invalid_email(api_client, user_payload):
    # Probando que creación rechaza email inválido con error de validación
    response = api_client.post(USERS_URL, json={**user_payload, "email": "invalid-email"})

    assert_validation_error(response, "email")


# Se fuerza una falla del repositorio para validar la response 503
def test_database_errors_return_service_unavailable(caplog):
    class FailingRepository:
        def list_users(self, limit: int, offset: int):
            raise SQLAlchemyError("database is unavailable")

    caplog.set_level(logging.CRITICAL, logger="app.core.exception_handlers")
    app.dependency_overrides[provide_user_repository] = lambda: FailingRepository()

    try:
        with TestClient(app) as client:
            response = client.get(USERS_URL)
    finally:
        app.dependency_overrides.clear()

    assert_detail_response(response, 503, "Database service unavailable")
