"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core.settings.database import DatabaseSettings
from core.settings.general import GeneralSettings
from fastapi import FastAPI
from src.api import api_router
from src.api.exceptions import register_exception_handlers
from src.connectors.database.services.users import UserDatabaseConnector
from src.services.users.service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Initialize shared services and dispose resources on shutdown.

    :param app: FastAPI application instance.
    :yields: Control back to the application runtime.
    """
    database_settings = DatabaseSettings()
    general_settings = GeneralSettings()
    user_database = UserDatabaseConnector(
        host=database_settings.host,
        port=database_settings.port,
        username=database_settings.username,
        password=database_settings.password,
        database=database_settings.database,
    )
    app.state.settings = general_settings
    app.state.user_service = UserService(user_database, general_settings)
    try:
        yield
    finally:
        await user_database.close()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    :returns: Configured FastAPI instance.
    """
    app = FastAPI(lifespan=lifespan)

    register_exception_handlers(app)
    app.include_router(api_router)
    return app
