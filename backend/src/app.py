"""FastAPI application factory."""

from fastapi import FastAPI
from src.api import api_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    :returns: Configured FastAPI instance.
    """
    app = FastAPI()

    app.include_router(api_router)
    return app
