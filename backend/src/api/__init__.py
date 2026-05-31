"""Root API router."""

from fastapi import APIRouter
from src.api.ping import router as ping_router

api_router = APIRouter(prefix='/api')
api_router.include_router(ping_router)

__all__ = ['api_router']
