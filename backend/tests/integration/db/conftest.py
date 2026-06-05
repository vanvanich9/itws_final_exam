"""Fixtures for database integration tests."""

import uuid

import pytest
from core.settings.database import DatabaseSettings
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from src.connectors.database.services.tasks import TaskDatabaseConnector
from src.connectors.database.services.users import UserDatabaseConnector


@pytest.fixture
def initial_migration_revision() -> str:
    """
    Return expected initial Alembic revision.

    :returns: Initial migration revision identifier.
    """
    return '95ac95d36c67'


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


@pytest.fixture
async def user(user_connector: UserDatabaseConnector):
    """
    Create a test user.

    :param user_connector: User database connector.
    :returns: Created user.
    """
    suffix = uuid.uuid4().hex[:8]
    return await user_connector.create(
        email=f'test-{suffix}@example.com',
        password='secret',
        name='Test User',
    )


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
