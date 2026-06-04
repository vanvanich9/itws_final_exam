"""User endpoints."""

from uuid import UUID

from core.config.enums import TokenType
from core.settings.general import GeneralSettings
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from src.api.dependencies import (
    get_current_user,
    get_settings,
    get_user_service,
    same_user,
)
from src.connectors.database.models import User
from src.logic.api import clear_refresh_cookie, set_refresh_cookie
from src.schemas.users import (
    LoginRequest,
    RegisterRequest,
    SuccessResponse,
    TokenResponse,
    UpdateUserRequest,
    UserResponse,
)
from src.services.users.service import UserService

router = APIRouter(prefix='/users', tags=['users'])


@router.post(
    '/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterRequest,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Register a new user.

    :param body: Registration payload.
    :param user_service: User service dependency.
    :returns: Created user.
    """
    user = await user_service.create(body.email, body.password, body.name)
    return UserResponse.model_validate(user)


@router.get('/me', response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Return the current user's profile.

    :param current_user: Authenticated user dependency.
    :returns: Current user data.
    """
    return UserResponse.model_validate(current_user)


@router.get('/{user_id}', response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    _current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Return a user profile by identifier.

    Any authenticated user can view any profile in the system.

    :param user_id: Target user identifier.
    :param user_service: User service dependency.
    :param _current_user: Ensures the request is authenticated.
    :returns: User data.
    """
    user = await user_service.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.put('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: UUID,
    body: UpdateUserRequest,
    _current_user: User = Depends(same_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Update a user profile by identifier.

    Only the user themselves can update their profile.

    :param user_id: Target user identifier.
    :param body: Fields to update.
    :param _current_user: Ensures the caller updates only their own profile.
    :param user_service: User service dependency.
    :returns: Updated user data.
    """
    user = await user_service.update(
        user_id,
        email=body.email,
        password=body.password,
        name=body.name,
    )
    return UserResponse.model_validate(user)


@router.delete('/{user_id}', response_model=UserResponse)
async def delete_user(
    user_id: UUID,
    _current_user: User = Depends(same_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Delete a user profile by identifier.

    Only the user themselves can delete their profile.

    :param user_id: Target user identifier.
    :param _current_user: Ensures the caller deletes only their own profile.
    :param user_service: User service dependency.
    :returns: Deleted user data.
    """
    user = await user_service.delete(user_id)
    return UserResponse.model_validate(user)


@router.post('/login', response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    user_service: UserService = Depends(get_user_service),
    settings: GeneralSettings = Depends(get_settings),
) -> TokenResponse:
    """
    Authenticate a user and return a JWT.

    Refresh token is set in an HTTP-only cookie.

    :param body: Login credentials.
    :param response: Outgoing HTTP response.
    :param user_service: User service dependency.
    :param settings: Application settings dependency.
    :returns: Issued token.
    """
    tokens = await user_service.authenticate(body.email, body.password)
    set_refresh_cookie(response, tokens.refresh_token, settings)
    return TokenResponse(token=tokens.access_token)


@router.post('/refresh', response_model=TokenResponse)
async def refresh_tokens(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias=TokenType.REFRESH,
    ),
    user_service: UserService = Depends(get_user_service),
    settings: GeneralSettings = Depends(get_settings),
) -> TokenResponse:
    """
    Reissue tokens using the refresh token cookie.

    :param response: Outgoing HTTP response.
    :param refresh_token: Refresh JWT from cookie.
    :param user_service: User service dependency.
    :param settings: Application settings dependency.
    :returns: New token.
    :raises HTTPException: When the refresh cookie is missing.
    """
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token is missing',
        )
    tokens = user_service.refresh_tokens(refresh_token)
    set_refresh_cookie(response, tokens.refresh_token, settings)
    return TokenResponse(token=tokens.access_token)


@router.post('/logout', response_model=SuccessResponse)
async def logout(
    response: Response,
    settings: GeneralSettings = Depends(get_settings),
) -> SuccessResponse:
    """
    Log out the user by clearing the refresh token cookie.

    :param response: Outgoing HTTP response.
    :param settings: Application settings dependency.
    :returns: Success flag.
    """
    clear_refresh_cookie(response, settings)
    return SuccessResponse()
