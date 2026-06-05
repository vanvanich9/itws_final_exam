"""User API schemas."""

from datetime import datetime
from uuid import UUID

from core.config.openapi import EXAMPLE_UUID
from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Credentials for user authentication."""

    email: str = Field(
        examples=['user@example.com'],
        description='Registered email address.',
    )
    password: str = Field(
        examples=['Secret@123'],
        description='Account password.',
    )


class RegisterRequest(BaseModel):
    """Payload for user registration."""

    email: str = Field(
        examples=['user@example.com'],
        description='Unique email address.',
    )
    password: str = Field(
        examples=['Secret@123'],
        description='Password (8-20 chars, mixed case, digit, special).',
    )
    name: str = Field(
        examples=['Jane Doe'],
        description='Display name.',
    )


class UpdateUserRequest(BaseModel):
    """Payload for updating a user profile."""

    email: str | None = Field(
        default=None,
        examples=['new@example.com'],
        description='New email, if changing.',
    )
    password: str | None = Field(
        default=None,
        examples=['NewSecret@1'],
        description='New password, if changing.',
    )
    name: str | None = Field(
        default=None,
        examples=['Jane Smith'],
        description='New display name, if changing.',
    )


class UserResponse(BaseModel):
    """Public user data returned by the API."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': EXAMPLE_UUID,
                'email': 'user@example.com',
                'name': 'Jane Doe',
                'created_at': '2024-01-01T12:00:00',
                'updated_at': '2024-01-02T12:00:00',
            },
        },
    )

    id: UUID = Field(description='User identifier.')
    email: str = Field(description='Email address.')
    name: str = Field(description='Display name.')
    created_at: datetime = Field(description='Account creation time (UTC).')
    updated_at: datetime = Field(description='Last profile update time (UTC).')


class TokenResponse(BaseModel):
    """JWT returned in response body."""

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            },
        },
    )

    token: str = Field(description='Bearer access token (JWT).')


class SuccessResponse(BaseModel):
    """Generic success flag for simple API actions."""

    model_config = ConfigDict(
        json_schema_extra={'example': {'success': True}},
    )

    success: bool = Field(
        default=True,
        description='Whether the operation completed successfully.',
    )
