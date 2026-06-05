"""FastAPI dependency providers."""

from uuid import UUID

from core.config.dependencies import BEARER_SCHEME
from core.config.enums import TokenType
from core.settings.general import GeneralSettings
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from src.connectors.database.models import Task, User
from src.logic.auth import validate_token
from src.services.tasks.errors import TaskNotFoundError
from src.services.tasks.service import TaskService
from src.services.users.service import UserService


def get_settings(request: Request) -> GeneralSettings:
    """
    Return application settings from request state.

    :param request: Incoming HTTP request.
    :returns: General settings instance.
    """
    return request.app.state.settings


def get_user_service(request: Request) -> UserService:
    """
    Return the user service from request state.

    :param request: Incoming HTTP request.
    :returns: User service instance.
    """
    return request.app.state.user_service


def get_task_service(request: Request) -> TaskService:
    """
    Return the task service from request state.

    :param request: Incoming HTTP request.
    :returns: Task service instance.
    """
    return request.app.state.task_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        BEARER_SCHEME,
    ),
    user_service: UserService = Depends(get_user_service),
    settings: GeneralSettings = Depends(get_settings),
) -> User:
    """
    Authenticate a request using a Bearer access token.

    :param credentials: Authorization header credentials.
    :param user_service: User service dependency.
    :param settings: Application settings dependency.
    :returns: Authenticated user.
    :raises HTTPException: When the access token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
        )
    payload = validate_token(
        credentials.credentials,
        settings.secret_key,
        token_type=TokenType.ACCESS,
    )
    return await user_service.get_by_id(payload.user_id)


async def same_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the authenticated user matches the path user identifier.

    :param user_id: Target user identifier from the path.
    :param current_user: Authenticated user dependency.
    :returns: Authenticated user when ids match.
    :raises HTTPException: When the caller acts on another user's resource.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can only access your own profile',
        )
    return current_user


async def get_owned_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> Task:
    """
    Load a task and ensure it belongs to the authenticated user.

    :param task_id: Task identifier from the path.
    :param current_user: Authenticated user dependency.
    :param task_service: Task service dependency.
    :returns: Task owned by the current user.
    :raises HTTPException: When the task is missing or owned by another user.
    """
    try:
        task = await task_service.get_by_id(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can only access your own tasks',
        )
    return task
