"""Integration test fixtures."""

import uuid

import httpx
import pytest
from core.settings.database import DatabaseSettings
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from src.connectors.database.services.tasks import TaskDatabaseConnector
from src.connectors.database.services.users import UserDatabaseConnector
from tests.settings import ApiTestSettings


@pytest.fixture
def initial_migration_revision() -> str:
    """
    Return expected initial Alembic revision.

    :returns: Initial migration revision identifier.
    """
    return '95ac95d36c67'


@pytest.fixture
def test_settings() -> ApiTestSettings:
    """
    Build API test settings from environment.

    :returns: API test settings instance.
    """
    return ApiTestSettings()


@pytest.fixture
async def api_client(test_settings: ApiTestSettings):
    """
    Provide async HTTP client for API tests.

    :param test_settings: API test settings.
    :yields: Configured HTTP client.
    """
    async with httpx.AsyncClient(
        base_url=test_settings.api_url,
        timeout=test_settings.api_timeout,
    ) as client:
        yield client


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


@pytest.fixture
async def db_engine(database_settings: DatabaseSettings) -> AsyncEngine:
    """
    Provide async SQLAlchemy engine for schema checks.

    :param database_settings: Database settings instance.
    :yields: Async database engine.
    """
    engine = create_async_engine(database_settings.url)
    yield engine
    await engine.dispose()


@pytest.fixture
async def user(user_connector: UserDatabaseConnector):
    """
    Create a test user.

    :param user_connector: User database connector.
    :returns: Created user.
    """
    suffix = uuid.uuid4().hex[:8]
    row = await user_connector.create(
        email=f'test-{suffix}@example.com',
        password='secret',
        name='Test User',
    )
    return row


@pytest.fixture
async def task(task_connector: TaskDatabaseConnector, user):
    """
    Create a test task for the given user.

    :param task_connector: Task database connector.
    :param user: Owner user.
    :returns: Created task.
    """
    return await task_connector.create(
        user_id=user.id,
        title='Test task',
        description='Test description',
    )


@pytest.fixture
async def migrated_schema(db_engine: AsyncEngine):
    """
    Inspect applied migrations and existing tables.

    :param db_engine: Async database engine.
    :returns: Alembic version and table names.
    """
    async with db_engine.connect() as conn:
        version = await conn.scalar(
            text('SELECT version_num FROM alembic_version')
        )

        def _inspect_tables(sync_conn):
            """
            Read table names from database metadata.

            :param sync_conn: Synchronous SQLAlchemy connection.
            :returns: Existing table names.
            """
            return inspect(sync_conn).get_table_names()

        tables = await conn.run_sync(_inspect_tables)

    return version, tables
