from app.modules.users.domain.entities import User
from app.modules.users.presentation.schemas import UserDeleteResponse, UserResponse

USER_DELETED_MESSAGE = "User deleted successfully"


def present_user(user: User) -> UserResponse:
    return UserResponse.model_validate(user)


def present_users(users: list[User]) -> list[UserResponse]:
    return [present_user(user) for user in users]


def present_user_deleted() -> UserDeleteResponse:
    return UserDeleteResponse(detail=USER_DELETED_MESSAGE)
