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
    return '95ac95d36c67'


@pytest.fixture
def test_settings() -> ApiTestSettings:
    return ApiTestSettings()


@pytest.fixture
async def api_client(test_settings: ApiTestSettings):
    async with httpx.AsyncClient(
        base_url=test_settings.api_url,
        timeout=test_settings.api_timeout,
    ) as client:
        yield client


@pytest.fixture
def database_settings() -> DatabaseSettings:
    return DatabaseSettings()


@pytest.fixture
def connector_kwargs(
    database_settings: DatabaseSettings,
) -> dict[str, str | int]:
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
    return UserDatabaseConnector(**connector_kwargs)


@pytest.fixture
def task_connector(
    connector_kwargs: dict[str, str | int],
) -> TaskDatabaseConnector:
    return TaskDatabaseConnector(**connector_kwargs)


@pytest.fixture
async def db_engine(database_settings: DatabaseSettings) -> AsyncEngine:
    engine = create_async_engine(database_settings.url)
    yield engine
    await engine.dispose()


@pytest.fixture
async def user(user_connector: UserDatabaseConnector):
    suffix = uuid.uuid4().hex[:8]
    row = await user_connector.create(
        email=f'test-{suffix}@example.com',
        password='secret',
        name='Test User',
    )
    return row


@pytest.fixture
async def task(task_connector: TaskDatabaseConnector, user):
    return await task_connector.create(
        user_id=user.id,
        title='Test task',
        description='Test description',
    )


@pytest.fixture
async def migrated_schema(db_engine: AsyncEngine):
    async with db_engine.connect() as conn:
        version = await conn.scalar(
            text('SELECT version_num FROM alembic_version')
        )

        def _inspect_tables(sync_conn):
            return inspect(sync_conn).get_table_names()

        tables = await conn.run_sync(_inspect_tables)

    return version, tables
