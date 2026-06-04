"""Password hashing, verification, credential validation, and JWT crypto."""

from datetime import UTC, datetime
from uuid import UUID

import bcrypt
import jwt
from core.config.auth import (
    EMAIL_ADAPTER,
    JWT_ALGORITHM,
    PASSWORD_PATTERN,
    TOKEN_TTL,
)
from core.config.enums import TokenType
from pydantic import ValidationError
from src.logic.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenTypeError,
)
from src.logic.models import TokenPair, TokenPayload


def is_valid_email(email: str) -> bool:
    """
    Check whether the email address is correctly formatted.

    :param email: Email address to validate.
    :returns: True when the email is valid, otherwise False.
    """
    try:
        EMAIL_ADAPTER.validate_python(email)
        return True
    except ValidationError:
        return False


def is_valid_password(password: str) -> bool:
    """
    Check password strength rules.

    Password must contain a lowercase letter, an uppercase letter,
    a special character, and be 8 to 20 characters long.

    :param password: Plain-text password to validate.
    :returns: True when the password meets all rules, otherwise False.
    """
    return PASSWORD_PATTERN.fullmatch(password) is not None


def hash_password(plain: str) -> str:
    """
    Hash a plain-text password.

    :param plain: Plain-text password.
    :returns: Bcrypt password hash.
    """
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a hash.

    :param plain: Plain-text password.
    :param hashed: Stored password hash.
    :returns: Whether the password matches.
    """
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:
        return False


def _create_token(
    user_id: UUID,
    secret_key: str,
    token_type: TokenType,
) -> str:
    """
    Encode a signed JWT for the given user.

    :param user_id: User identifier stored in the token payload.
    :param secret_key: Secret used to sign the token.
    :param token_type: Token purpose marker (access or refresh).
    :returns: Encoded JWT string.
    """
    now = datetime.now(UTC)
    payload = {
        'user_id': str(user_id),
        'type': token_type.value,
        'iat': now,
        'exp': now + TOKEN_TTL[token_type],
    }
    return jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)


def decode_token(token: str, secret_key: str) -> TokenPayload:
    """
    Decode and validate a signed JWT.

    :param token: Encoded JWT string.
    :param secret_key: Secret used to verify the token signature.
    :returns: Parsed token payload.
    :raises ExpiredTokenError: When the token has expired.
    :raises InvalidTokenError: When the token is malformed or invalid.
    """
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise ExpiredTokenError from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError from exc

    try:
        return TokenPayload(
            user_id=UUID(payload['user_id']),
            token_type=TokenType(payload['type']),
            issued_at=payload['iat'],
            expires_at=payload['exp'],
        )
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        raise InvalidTokenError from exc


def validate_token(
    token: str,
    secret_key: str,
    token_type: TokenType,
) -> TokenPayload:
    """
    Decode a JWT and verify it matches the expected type.

    :param token: Encoded JWT string.
    :param secret_key: Secret used to verify the token signature.
    :param token_type: Expected token purpose marker.
    :returns: Parsed token payload.
    :raises ExpiredTokenError: When the token has expired.
    :raises InvalidTokenTypeError: When the token type does not match.
    :raises InvalidTokenError: When the token is malformed or invalid.
    """
    payload = decode_token(token, secret_key)
    if payload.token_type is not token_type:
        raise InvalidTokenTypeError
    return payload


def create_access_token(user_id: UUID, secret_key: str) -> str:
    """
    Issue a short-lived access JWT.

    :param user_id: Authenticated user identifier.
    :param secret_key: Secret used to sign the token.
    :returns: Encoded access token.
    """
    return _create_token(
        user_id,
        secret_key=secret_key,
        token_type=TokenType.ACCESS,
    )


def create_refresh_token(user_id: UUID, secret_key: str) -> str:
    """
    Issue a long-lived refresh JWT.

    :param user_id: Authenticated user identifier.
    :param secret_key: Secret used to sign the token.
    :returns: Encoded refresh token.
    """
    return _create_token(
        user_id,
        secret_key=secret_key,
        token_type=TokenType.REFRESH,
    )


def issue_tokens(user_id: UUID, secret_key: str) -> TokenPair:
    """
    Issue access and refresh JWT tokens for a user.

    Access token lives 5 minutes, refresh token lives 60 minutes.

    :param user_id: Authenticated user identifier.
    :param secret_key: Secret used to sign tokens.
    :returns: Access and refresh token pair.
    """
    return TokenPair(
        access_token=create_access_token(user_id, secret_key),
        refresh_token=create_refresh_token(user_id, secret_key),
    )
