"""Unit tests for logic and service error classes and data models."""

import uuid
from datetime import UTC, datetime

from core.config.enums import TokenType
from src.logic.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenTypeError,
)
from src.logic.models import TokenPair, TokenPayload
from src.services.tasks.errors import InvalidTitleError, TaskNotFoundError
from src.services.users.errors import (
    InvalidEmailError,
    InvalidPasswordError,
    PasswordMismatchError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


def test_token_error_default_messages():
    """Verify token errors expose their default messages."""
    assert str(InvalidTokenError()) == 'Invalid token'
    assert str(ExpiredTokenError()) == 'Token expired'
    assert str(InvalidTokenTypeError()) == 'Invalid token type'


def test_token_error_hierarchy():
    """Verify expired and type errors derive from the base token error."""
    assert issubclass(ExpiredTokenError, InvalidTokenError)
    assert issubclass(InvalidTokenTypeError, InvalidTokenError)


def test_service_error_default_messages():
    """Verify service errors expose their default messages."""
    assert str(InvalidEmailError()) == 'Incorrect email'
    assert str(InvalidPasswordError()) == 'Incorrect password'
    assert str(InvalidTitleError()) == 'Incorrect title'
    assert str(UserNotFoundError()) == 'user not found'
    assert str(TaskNotFoundError()) == 'task not found'
    assert str(PasswordMismatchError()) == 'incorrect password'
    assert str(UserAlreadyExistsError()) == 'user already exists'


def test_token_pair_model():
    """Verify the token pair model stores both tokens."""
    pair = TokenPair(access_token='acc', refresh_token='ref')

    assert pair.access_token == 'acc'
    assert pair.refresh_token == 'ref'


def test_token_payload_model():
    """Verify the token payload model parses claim fields."""
    user_id = uuid.uuid4()
    now = datetime.now(UTC)

    payload = TokenPayload(
        user_id=user_id,
        token_type=TokenType.ACCESS,
        issued_at=now,
        expires_at=now,
    )

    assert payload.user_id == user_id
    assert payload.token_type is TokenType.ACCESS
