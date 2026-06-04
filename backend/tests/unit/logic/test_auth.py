"""Unit tests for authentication logic (hashing, validation, JWT)."""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from core.config.auth import JWT_ALGORITHM
from core.config.enums import TokenType
from src.logic.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_valid_email,
    is_valid_password,
    issue_tokens,
    validate_token,
    verify_password,
)
from src.logic.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenTypeError,
)
from src.logic.models import TokenPair, TokenPayload


def test_hash_password_is_not_plaintext():
    """Verify hashing returns a value different from the input."""
    hashed = hash_password('Secret@123')

    assert hashed != 'Secret@123'
    assert isinstance(hashed, str)


def test_verify_password_matches_hash():
    """Verify a correct password verifies against its hash."""
    hashed = hash_password('Secret@123')

    assert verify_password('Secret@123', hashed) is True


def test_verify_password_rejects_wrong_password():
    """Verify an incorrect password fails verification."""
    hashed = hash_password('Secret@123')

    assert verify_password('Wrong@123', hashed) is False


def test_verify_password_handles_malformed_hash():
    """Verify malformed hashes return False instead of raising."""
    assert verify_password('Secret@123', 'not-a-bcrypt-hash') is False


@pytest.mark.parametrize(
    'email',
    ['user@example.com', 'a.b-c@sub.domain.io'],
)
def test_is_valid_email_accepts_valid(email):
    """
    Verify valid email addresses pass validation.

    :param email: Email address under test.
    """
    assert is_valid_email(email) is True


@pytest.mark.parametrize(
    'email',
    ['not-an-email', 'missing@tld', '@no-local.com', ''],
)
def test_is_valid_email_rejects_invalid(email):
    """
    Verify invalid email addresses fail validation.

    :param email: Email address under test.
    """
    assert is_valid_email(email) is False


@pytest.mark.parametrize(
    'password',
    ['Secret@123', 'Aa!aaaa1', 'Zz9$zzzzzzzzzzzzzzz0'],
)
def test_is_valid_password_accepts_strong(password):
    """
    Verify strong passwords pass validation.

    :param password: Password under test.
    """
    assert is_valid_password(password) is True


@pytest.mark.parametrize(
    'password',
    [
        'Aa1@',
        'Aa1@' + 'a' * 20,
        'SECRET@123',
        'secret@123',
        'Secret@abc',
        'Secret1234',
    ],
)
def test_is_valid_password_rejects_weak(password):
    """
    Verify weak passwords fail validation.

    :param password: Password under test.
    """
    assert is_valid_password(password) is False


def test_create_and_decode_access_token(secret_key):
    """
    Verify an access token decodes to the expected payload.

    :param secret_key: Signing secret fixture.
    """
    user_id = uuid.uuid4()
    token = create_access_token(user_id, secret_key)

    payload = decode_token(token, secret_key)

    assert isinstance(payload, TokenPayload)
    assert payload.user_id == user_id
    assert payload.token_type is TokenType.ACCESS


def test_create_and_decode_refresh_token(secret_key):
    """
    Verify a refresh token decodes with the refresh type.

    :param secret_key: Signing secret fixture.
    """
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id, secret_key)

    payload = decode_token(token, secret_key)

    assert payload.user_id == user_id
    assert payload.token_type is TokenType.REFRESH


def test_validate_token_accepts_matching_type(secret_key):
    """
    Verify validate_token returns payload for the expected type.

    :param secret_key: Signing secret fixture.
    """
    user_id = uuid.uuid4()
    token = create_access_token(user_id, secret_key)

    payload = validate_token(token, secret_key, token_type=TokenType.ACCESS)

    assert payload.user_id == user_id


def test_validate_token_rejects_wrong_type(secret_key):
    """
    Verify validate_token raises when the type does not match.

    :param secret_key: Signing secret fixture.
    """
    token = create_access_token(uuid.uuid4(), secret_key)

    with pytest.raises(InvalidTokenTypeError):
        validate_token(token, secret_key, token_type=TokenType.REFRESH)


def test_decode_token_rejects_garbage(secret_key):
    """
    Verify malformed tokens raise InvalidTokenError.

    :param secret_key: Signing secret fixture.
    """
    with pytest.raises(InvalidTokenError):
        decode_token('not.a.jwt', secret_key)


def test_decode_token_rejects_wrong_secret(secret_key):
    """
    Verify a bad signature raises InvalidTokenError.

    :param secret_key: Signing secret fixture.
    """
    token = create_access_token(uuid.uuid4(), secret_key)

    with pytest.raises(InvalidTokenError):
        decode_token(token, 'a-different-secret-key-long-enough-for-hs256')


def test_decode_token_rejects_expired(secret_key):
    """
    Verify expired tokens raise ExpiredTokenError.

    :param secret_key: Signing secret fixture.
    """
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            'user_id': str(uuid.uuid4()),
            'type': TokenType.ACCESS.value,
            'iat': now - timedelta(minutes=10),
            'exp': now - timedelta(minutes=5),
        },
        secret_key,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(ExpiredTokenError):
        decode_token(token, secret_key)


def test_decode_token_rejects_missing_claims(secret_key):
    """
    Verify tokens missing required claims raise InvalidTokenError.

    :param secret_key: Signing secret fixture.
    """
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            'type': TokenType.ACCESS.value,
            'iat': now,
            'exp': now + timedelta(minutes=5),
        },
        secret_key,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(InvalidTokenError):
        decode_token(token, secret_key)


def test_decode_token_rejects_unknown_type(secret_key):
    """
    Verify tokens with an unknown type claim raise InvalidTokenError.

    :param secret_key: Signing secret fixture.
    """
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            'user_id': str(uuid.uuid4()),
            'type': 'bogus',
            'iat': now,
            'exp': now + timedelta(minutes=5),
        },
        secret_key,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(InvalidTokenError):
        decode_token(token, secret_key)


def test_issue_tokens_returns_valid_pair(secret_key):
    """
    Verify issue_tokens returns a decodable access/refresh pair.

    :param secret_key: Signing secret fixture.
    """
    user_id = uuid.uuid4()

    pair = issue_tokens(user_id, secret_key)

    assert isinstance(pair, TokenPair)
    access_payload = validate_token(
        pair.access_token,
        secret_key,
        token_type=TokenType.ACCESS,
    )
    refresh_payload = validate_token(
        pair.refresh_token,
        secret_key,
        token_type=TokenType.REFRESH,
    )
    assert access_payload.user_id == user_id
    assert refresh_payload.user_id == user_id
