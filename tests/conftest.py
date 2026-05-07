from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.users.domain.entities import User
from app.modules.users.domain.enums import UserRole
from app.modules.users.domain.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.modules.users.presentation.providers import provide_user_repository


def utc_now() -> datetime:
    return datetime.now(UTC)


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[int, User] = {}
        self.next_id = 1

    def add_user(
        self,
        *,
        username: str,
        email: str,
        first_name: str = "Test",
        last_name: str = "User",
        role: UserRole = UserRole.USER,
        active: bool = True,
    ) -> User:
        user = User(
            id=self.next_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            active=active,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        self.users[user.id] = user
        self.next_id += 1
        return user

    def create(self, user: User) -> User:
        if self.get_by_username(user.username) or self.get_by_email(user.email):
            raise UserAlreadyExistsError()

        return self.add_user(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            active=user.active,
        )

    def get_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    def get_by_username(self, username: str) -> User | None:
        return next(
            (user for user in self.users.values() if user.username == username),
            None,
        )

    def list_users(self, limit: int, offset: int) -> list[User]:
        return list(self.users.values())[offset : offset + limit]

    def update(self, user: User) -> User:
        if user.id is None or user.id not in self.users:
            raise UserNotFoundError()

        updated_user = replace(user, updated_at=utc_now())
        self.users[user.id] = updated_user
        return updated_user

    def delete(self, user_id: int) -> None:
        self.users.pop(user_id, None)


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def api_client(user_repository: InMemoryUserRepository) -> TestClient:
    def override_user_repository() -> InMemoryUserRepository:
        return user_repository

    app.dependency_overrides[provide_user_repository] = override_user_repository

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user_payload() -> dict[str, Any]:
    return {
        "username": "jane.doe",
        "email": "jane.doe@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "user",
        "active": True,
    }
