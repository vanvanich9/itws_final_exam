"""Integration test fixtures shared across API and database tests."""

import pytest
from core.settings.database import DatabaseSettings
from src.connectors.database.services.tasks import TaskDatabaseConnector
from src.connectors.database.services.users import UserDatabaseConnector


@pytest.fixture
def database_settings() -> DatabaseSettings:
    """
    Build database settings from environment.

    :returns: Database settings instance.
    """
    return DatabaseSettings()


@pytest.fixture
def connector_kwargs(
    database_settings: DatabaseSettings,
) -> dict[str, str | int]:
    """
    Build database connector keyword arguments.

    :param database_settings: Database settings instance.
    :returns: Connector initialization kwargs.
    """
    return {
        'host': database_settings.host,
        'port': database_settings.port,
        'username': database_settings.username,
        'password': database_settings.password,
        'database': database_settings.database,
    }


@pytest.fixture
def user_connector(
    connector_kwargs: dict[str, str | int],
) -> UserDatabaseConnector:
    """
    Provide user database connector.

    :param connector_kwargs: Connector initialization kwargs.
    :returns: User database connector.
    """
    return UserDatabaseConnector(**connector_kwargs)


@pytest.fixture
def task_connector(
    connector_kwargs: dict[str, str | int],
) -> TaskDatabaseConnector:
    """
    Provide task database connector.

    :param connector_kwargs: Connector initialization kwargs.
    :returns: Task database connector.
    """
    return TaskDatabaseConnector(**connector_kwargs)
