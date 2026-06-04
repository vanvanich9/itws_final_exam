"""Unit tests for HTTP cookie helpers."""

from types import SimpleNamespace

from core.config.auth import TOKEN_TTL
from core.config.enums import TokenType
from fastapi import Response
from src.logic.api import clear_refresh_cookie, set_refresh_cookie
from tests.utils.funcs import set_cookie_header


def test_set_refresh_cookie_sets_expected_attributes():
    """Verify the refresh cookie carries security attributes."""
    response = Response()
    settings = SimpleNamespace(debug=True)

    set_refresh_cookie(response, 'refresh-jwt', settings)

    header = set_cookie_header(response)
    max_age = int(TOKEN_TTL[TokenType.REFRESH].total_seconds())
    assert f'{TokenType.REFRESH.value}=refresh-jwt' in header
    assert 'HttpOnly' in header
    assert 'SameSite=lax' in header
    assert f'Max-Age={max_age}' in header


def test_set_refresh_cookie_secure_when_not_debug():
    """Verify the Secure flag is set when debug is disabled."""
    response = Response()
    settings = SimpleNamespace(debug=False)

    set_refresh_cookie(response, 'refresh-jwt', settings)

    assert 'Secure' in set_cookie_header(response)


def test_set_refresh_cookie_insecure_when_debug():
    """Verify the Secure flag is omitted when debug is enabled."""
    response = Response()
    settings = SimpleNamespace(debug=True)

    set_refresh_cookie(response, 'refresh-jwt', settings)

    assert 'Secure' not in set_cookie_header(response)


def test_clear_refresh_cookie_expires_cookie():
    """Verify clearing the cookie targets the refresh cookie name."""
    response = Response()
    settings = SimpleNamespace(debug=True)

    clear_refresh_cookie(response, settings)

    header = set_cookie_header(response)
    assert f'{TokenType.REFRESH.value}=' in header
    assert 'Max-Age=0' in header or 'expires=' in header.lower()
