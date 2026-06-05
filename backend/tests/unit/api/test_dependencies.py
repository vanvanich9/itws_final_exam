"""Unit tests for FastAPI dependency providers."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from src.api.dependencies import (
    get_current_user,
    get_settings,
    get_task_service,
    get_user_service,
    same_user,
)
from src.logic.auth import create_access_token, create_refresh_token
from src.logic.errors import InvalidTokenError, InvalidTokenTypeError
from tests.utils.funcs import request_with_state


def test_get_settings_reads_app_state():
    """Verify get_settings returns settings from app state."""
    sentinel = object()
    request = request_with_state(settings=sentinel)

    assert get_settings(request) is sentinel


def test_get_user_service_reads_app_state():
    """Verify get_user_service returns the service from app state."""
    sentinel = object()
    request = request_with_state(user_service=sentinel)

    assert get_user_service(request) is sentinel


def test_get_task_service_reads_app_state():
    """Verify get_task_service returns the service from app state."""
    sentinel = object()
    request = request_with_state(task_service=sentinel)

    assert get_task_service(request) is sentinel


async def test_get_current_user_requires_credentials(secret_key):
    """
    Verify a missing Authorization header raises 401.

    :param secret_key: Signing secret fixture.
    """
    settings = SimpleNamespace(secret_key=secret_key)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            credentials=None,
            user_service=AsyncMock(),
            settings=settings,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_current_user_returns_user(secret_key, make_user):
    """
    Verify a valid access token resolves to the stored user.

    :param secret_key: Signing secret fixture.
    :param make_user: User factory fixture.
    """
    user = make_user()
    service = AsyncMock()
    service.get_by_id.return_value = user
    settings = SimpleNamespace(secret_key=secret_key)
    token = create_access_token(user.id, secret_key)
    credentials = HTTPAuthorizationCredentials(
        scheme='Bearer',
        credentials=token,
    )

    result = await get_current_user(
        credentials=credentials,
        user_service=service,
        settings=settings,
    )

    assert result is user
    service.get_by_id.assert_awaited_once_with(user.id)


async def test_get_current_user_rejects_invalid_token(secret_key):
    """
    Verify a malformed token raises InvalidTokenError.

    :param secret_key: Signing secret fixture.
    """
    settings = SimpleNamespace(secret_key=secret_key)
    credentials = HTTPAuthorizationCredentials(
        scheme='Bearer',
        credentials='garbage.token',
    )

    with pytest.raises(InvalidTokenError):
        await get_current_user(
            credentials=credentials,
            user_service=AsyncMock(),
            settings=settings,
        )


async def test_get_current_user_rejects_refresh_token(secret_key):
    """
    Verify a refresh token cannot be used as an access token.

    :param secret_key: Signing secret fixture.
    """
    settings = SimpleNamespace(secret_key=secret_key)
    token = create_refresh_token(uuid.uuid4(), secret_key)
    credentials = HTTPAuthorizationCredentials(
        scheme='Bearer',
        credentials=token,
    )

    with pytest.raises(InvalidTokenTypeError):
        await get_current_user(
            credentials=credentials,
            user_service=AsyncMock(),
            settings=settings,
        )


async def test_same_user_allows_matching_id(make_user):
    """
    Verify same_user returns the user when ids match.

    :param make_user: User factory fixture.
    """
    user = make_user()

    result = await same_user(user_id=user.id, current_user=user)

    assert result is user


async def test_same_user_rejects_mismatched_id(make_user):
    """
    Verify same_user raises 403 when ids differ.

    :param make_user: User factory fixture.
    """
    user = make_user()

    with pytest.raises(HTTPException) as exc_info:
        await same_user(user_id=uuid.uuid4(), current_user=user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
