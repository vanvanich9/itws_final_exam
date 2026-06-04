"""Fixtures for user service unit tests."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.services.users.service import UserService


@pytest.fixture
def connector() -> MagicMock:
    """
    Provide a mocked user database connector.

    :returns: Mock connector with async methods.
    """
    mock = MagicMock()
    mock.get_by_email = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture
def service(connector: MagicMock, secret_key: str) -> UserService:
    """
    Provide a user service backed by the mock connector.

    :param connector: Mock database connector.
    :param secret_key: Signing secret fixture.
    :returns: User service instance.
    """
    settings = SimpleNamespace(secret_key=secret_key)
    return UserService(connector, settings)
