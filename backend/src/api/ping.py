"""Ping health-check endpoint."""

from fastapi import APIRouter
from src.schemas.ping import PingResponse

router = APIRouter(prefix='/ping')


@router.get('/')
async def ping() -> PingResponse:
    """
    Return a pong response.

    :returns: Health-check payload.
    """
    return PingResponse()
