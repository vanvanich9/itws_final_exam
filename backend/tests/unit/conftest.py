"""Unit test fixtures."""

import uuid
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from src.api.dependencies import (
    get_current_user,
    get_settings,
    get_user_service,
)
from src.app import create_app
from tests.utils.constants import TEST_SECRET


@pytest.fixture
def secret_key() -> str:
    """
    Provide a deterministic secret key for JWT tests.

    :returns: Secret key string.
    """
    return TEST_SECRET


@pytest.fixture
def make_user():
    """
    Provide a factory building lightweight user-like objects.

    :returns: Factory producing user namespaces.
    """

    def _make(
        user_id: uuid.UUID | None = None,
        email: str = 'user@example.com',
        name: str = 'Test User',
    ) -> SimpleNamespace:
        """
        Build a user object compatible with UserResponse.

        :param user_id: Optional identifier, generated when omitted.
        :param email: User email.
        :param name: Display name.
        :returns: User-like namespace.
        """
        now = datetime(2024, 1, 1, 12, 0, 0)
        return SimpleNamespace(
            id=user_id or uuid.uuid4(),
            email=email,
            name=name,
            created_at=now,
            updated_at=now,
        )

    return _make


@pytest.fixture
def user_service_mock() -> MagicMock:
    """
    Provide a mocked user service matching endpoint call signatures.

    :returns: Mock user service.
    """
    service = MagicMock()
    service.create = AsyncMock()
    service.authenticate = AsyncMock()
    service.get_by_id = AsyncMock()
    service.update = AsyncMock()
    service.delete = AsyncMock()
    service.refresh_tokens = MagicMock()
    return service


@pytest.fixture
def settings_stub() -> SimpleNamespace:
    """
    Provide application settings stub for API dependencies.

    :returns: Settings namespace with debug and secret key.
    """
    return SimpleNamespace(debug=True, secret_key=TEST_SECRET)


@pytest.fixture
def app(user_service_mock: MagicMock, settings_stub: SimpleNamespace):
    """
    Build a FastAPI app with overridden service and settings deps.

    :param user_service_mock: Mock user service.
    :param settings_stub: Settings stub.
    :returns: Configured FastAPI application.
    """
    application = create_app()
    application.dependency_overrides[get_user_service] = lambda: (
        user_service_mock
    )
    application.dependency_overrides[get_settings] = lambda: settings_stub
    return application


@pytest.fixture
def authenticate_as(app):
    """
    Provide a helper overriding the current-user dependency.

    :param app: FastAPI application under test.
    :returns: Callable installing an authenticated user.
    """

    def _login(user: SimpleNamespace) -> SimpleNamespace:
        """
        Force the authenticated user for the app.

        :param user: User to authenticate as.
        :returns: The same user.
        """
        app.dependency_overrides[get_current_user] = lambda: user
        return user

    return _login


@pytest.fixture
async def client(app):
    """
    Provide an async HTTP client bound to the ASGI app.

    :param app: FastAPI application under test.
    :yields: Configured async client.
    """
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as http_client:
        yield http_client
