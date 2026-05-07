from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.modules.users.application.dto import (
    CreateUserDTO,
    UpdateUserDTO,
)
from app.modules.users.application.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from app.modules.users.presentation.openapi_responses import (
    CREATE_USER_RESPONSES,
    DELETE_USER_RESPONSES,
    GET_USER_RESPONSES,
    LIST_USERS_RESPONSES,
    PATCH_USER_RESPONSES,
    UPDATE_USER_RESPONSES,
)
from app.modules.users.presentation.presenters import (
    present_user,
    present_user_deleted,
    present_users,
)
from app.modules.users.presentation.providers import UserRepositoryDep
from app.modules.users.presentation.schemas import (
    UserCreateRequest,
    UserDeleteResponse,
    UserPatchRequest,
    UserUpdateRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


UserId = Annotated[int, Path(ge=1)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    responses=CREATE_USER_RESPONSES,
)
def create_user(
    request: UserCreateRequest,
    repository: UserRepositoryDep,
) -> UserResponse:
    dto = CreateUserDTO(**request.model_dump())
    user = CreateUserUseCase(repository).execute(dto)

    return present_user(user)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List users",
    responses=LIST_USERS_RESPONSES,
)
def list_users(
    repository: UserRepositoryDep,
    limit: Limit = 20,
    offset: Offset = 0,
) -> list[UserResponse]:
    users = ListUsersUseCase(repository).execute(limit=limit, offset=offset)

    return present_users(users)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
    responses=GET_USER_RESPONSES,
)
def get_user(
    user_id: UserId,
    repository: UserRepositoryDep,
) -> UserResponse:
    user = GetUserUseCase(repository).execute(user_id)

    return present_user(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    responses=UPDATE_USER_RESPONSES,
)
def update_user(
    user_id: UserId,
    request: UserUpdateRequest,
    repository: UserRepositoryDep,
) -> UserResponse:
    dto = UpdateUserDTO(**request.model_dump())
    user = UpdateUserUseCase(repository).execute(user_id, dto)

    return present_user(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Partially update a user",
    responses=PATCH_USER_RESPONSES,
)
def patch_user(
    user_id: UserId,
    request: UserPatchRequest,
    repository: UserRepositoryDep,
) -> UserResponse:
    dto = UpdateUserDTO(**request.model_dump(exclude_unset=True))
    user = UpdateUserUseCase(repository).execute(user_id, dto)

    return present_user(user)


@router.delete(
    "/{user_id}",
    response_model=UserDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
    responses=DELETE_USER_RESPONSES,
)
def delete_user(
    user_id: UserId,
    repository: UserRepositoryDep,
) -> UserDeleteResponse:
    DeleteUserUseCase(repository).execute(user_id)

    return present_user_deleted()
