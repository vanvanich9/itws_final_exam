"""Unit tests for user API schemas."""

import uuid
from datetime import datetime
from types import SimpleNamespace

from src.schemas.users import UpdateUserRequest, UserResponse


def test_user_response_from_attributes():
    """Verify UserResponse maps from an ORM-like object."""
    user_id = uuid.uuid4()
    created = datetime(2024, 1, 1, 10, 0, 0)
    updated = datetime(2024, 1, 2, 11, 0, 0)
    source = SimpleNamespace(
        id=user_id,
        email='user@example.com',
        name='Test User',
        created_at=created,
        updated_at=updated,
        password='should-not-leak',
    )

    response = UserResponse.model_validate(source)

    assert response.id == user_id
    assert response.email == 'user@example.com'
    assert response.name == 'Test User'
    assert response.created_at == created
    assert response.updated_at == updated


def test_user_response_excludes_password():
    """Verify the public schema does not expose the password field."""
    assert 'password' not in UserResponse.model_fields


def test_update_user_request_defaults_to_none():
    """Verify all update fields default to None."""
    body = UpdateUserRequest()

    assert body.email is None
    assert body.password is None
    assert body.name is None


def test_update_user_request_accepts_partial_payload():
    """Verify update request accepts a subset of fields."""
    body = UpdateUserRequest(name='New Name')

    assert body.name == 'New Name'
    assert body.email is None
    assert body.password is None
