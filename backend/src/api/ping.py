"""Ping health-check endpoint."""

from fastapi import APIRouter
from src.schemas.ping import PingResponse

router = APIRouter(prefix='/ping', tags=['Health'])


@router.get(
    '/',
    response_model=PingResponse,
    summary='Health check',
    description='Verify that the API is running.',
)
async def ping() -> PingResponse:
    """
    Return a pong response.

    :returns: Health-check payload.
    """
    return PingResponse()
