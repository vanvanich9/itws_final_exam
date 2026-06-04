"""User API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    """Credentials for user authentication."""

    email: str
    password: str


class RegisterRequest(BaseModel):
    """Payload for user registration."""

    email: str
    password: str
    name: str


class UpdateUserRequest(BaseModel):
    """Payload for updating a user profile."""

    email: str | None = None
    password: str | None = None
    name: str | None = None


class UserResponse(BaseModel):
    """Public user data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """JWT returned in response body."""

    token: str


class SuccessResponse(BaseModel):
    """Generic success flag for simple API actions."""

    success: bool = True
