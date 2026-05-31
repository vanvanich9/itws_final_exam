"""Ping API schemas."""

from pydantic import BaseModel


class PingResponse(BaseModel):
    """Response body for the ping endpoint."""

    message: str = 'pong'
