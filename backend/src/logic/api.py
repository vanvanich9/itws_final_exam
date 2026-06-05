"""HTTP helpers shared by API endpoints."""

from core.config.auth import TOKEN_TTL
from core.config.enums import TokenType
from core.settings.general import GeneralSettings
from fastapi import Response


def set_refresh_cookie(
    response: Response,
    refresh_token: str,
    settings: GeneralSettings,
) -> None:
    """
    Attach a refresh JWT to an HTTP-only cookie.

    :param response: Outgoing HTTP response.
    :param refresh_token: Encoded refresh token.
    :param settings: Application settings.
    """
    response.set_cookie(
        key=TokenType.REFRESH,
        value=refresh_token,
        httponly=True,
        secure=not settings.debug,
        samesite='lax',
        max_age=int(TOKEN_TTL[TokenType.REFRESH].total_seconds()),
    )


def clear_refresh_cookie(
    response: Response,
    settings: GeneralSettings,
) -> None:
    """
    Remove the refresh token cookie from the client.

    :param response: Outgoing HTTP response.
    :param settings: Application settings.
    """
    response.delete_cookie(
        key=TokenType.REFRESH,
        httponly=True,
        secure=not settings.debug,
        samesite='lax',
    )
