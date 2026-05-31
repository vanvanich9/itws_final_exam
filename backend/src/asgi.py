"""ASGI entrypoint for the application server."""

from src.app import create_app

app = create_app()
