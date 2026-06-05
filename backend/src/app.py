"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core.config.openapi import OPENAPI_TAGS
from core.settings.database import DatabaseSettings
from core.settings.general import GeneralSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import api_router
from src.api.exceptions import register_exception_handlers
from src.connectors.database.services.tasks import TaskDatabaseConnector
from src.connectors.database.services.users import UserDatabaseConnector
from src.services.tasks.service import TaskService
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
    connector_kwargs = {
        'host': database_settings.host,
        'port': database_settings.port,
        'username': database_settings.username,
        'password': database_settings.password,
        'database': database_settings.database,
    }
    user_database = UserDatabaseConnector(**connector_kwargs)
    task_database = TaskDatabaseConnector(**connector_kwargs)
    app.state.settings = general_settings
    app.state.user_service = UserService(user_database, general_settings)
    app.state.task_service = TaskService(task_database)
    try:
        yield
    finally:
        await user_database.close()
        await task_database.close()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    :returns: Configured FastAPI instance.
    """
    settings = GeneralSettings()

    app = FastAPI(
        title='Task Manager API',
        description=(
            'REST API for user accounts and personal task boards.\n\n'
            '**Authentication:** call `POST /api/users/login`, copy the '
            '`token` from the response, then click **Authorize** and paste '
            '`Bearer <token>` (or just the token, depending on the UI).\n\n'
            'The refresh token is stored in an HTTP-only cookie and is used '
            'by `POST /api/users/refresh`.'
        ),
        version='1.0.0',
        lifespan=lifespan,
        openapi_tags=OPENAPI_TAGS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app
