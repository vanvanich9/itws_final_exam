"""Logic layer data models."""

from datetime import datetime
from uuid import UUID

from core.config.enums import TokenType
from pydantic import BaseModel


class TokenPair(BaseModel):
    """Issued access and refresh JWT tokens."""

    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    """Decoded JWT claims used by auth logic."""

    user_id: UUID
    token_type: TokenType
    issued_at: datetime
    expires_at: datetime
