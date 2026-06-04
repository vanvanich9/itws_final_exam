"""Shared test helper functions."""

import uuid
from types import SimpleNamespace

import httpx
from fastapi import Response
from src.connectors.database.services.users import UserDatabaseConnector


def set_cookie_header(response: Response) -> str:
    """
    Read the Set-Cookie header from a response.

    :param response: Response carrying the cookie.
    :returns: Set-Cookie header value.
    """
    return response.headers['set-cookie']


def request_with_state(**state) -> SimpleNamespace:
    """
    Build a request-like object exposing app state.

    :param state: Attributes to attach to app state.
    :returns: Request namespace.
    """
    return SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(**state)),
    )


def bearer(token: str) -> dict[str, str]:
    """
    Build an Authorization header for a bearer token.

    :param token: Access token value.
    :returns: Header mapping with the bearer token.
    """
    return {'Authorization': f'Bearer {token}'}


def refresh_cookie(response: httpx.Response) -> str | None:
    """
    Extract the refresh token cookie value from a response.

    :param response: HTTP response carrying the cookie.
    :returns: Refresh token value when present, otherwise None.
    """
    value = response.cookies.get('refresh_token')
    if value:
        return value
    for header in response.headers.get_list('set-cookie'):
        if header.startswith('refresh_token='):
            return header.split('=', 1)[1].split(';', 1)[0]
    return None


async def create_other_user(
    user_connector: UserDatabaseConnector,
) -> object:
    """
    Create a distinct secondary user directly in the database.

    :param user_connector: User database connector.
    :returns: Created user instance.
    """
    suffix = uuid.uuid4().hex[:8]
    return await user_connector.create(
        email=f'other-{suffix}@example.com',
        password='secret',
        name='Other User',
    )
