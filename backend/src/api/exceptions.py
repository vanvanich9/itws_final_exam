"""API exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from src.logic.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenTypeError,
)
from src.services.tasks.errors import InvalidTitleError, TaskNotFoundError
from src.services.users.errors import (
    InvalidEmailError,
    InvalidPasswordError,
    PasswordMismatchError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register domain exception handlers on the FastAPI app.

    :param app: FastAPI application instance.
    """

    @app.exception_handler(UserNotFoundError)
    @app.exception_handler(PasswordMismatchError)
    @app.exception_handler(ExpiredTokenError)
    @app.exception_handler(InvalidTokenError)
    @app.exception_handler(InvalidTokenTypeError)
    async def unauthorized_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Map authentication failures to HTTP 401 responses.

        :param _request: Incoming HTTP request.
        :param exc: Raised domain exception.
        :returns: JSON error response.
        """
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': str(exc)},
        )

    @app.exception_handler(TaskNotFoundError)
    async def not_found_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Map missing task errors to HTTP 404 responses.

        :param _request: Incoming HTTP request.
        :param exc: Raised domain exception.
        :returns: JSON error response.
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'detail': str(exc)},
        )

    @app.exception_handler(InvalidEmailError)
    @app.exception_handler(InvalidPasswordError)
    @app.exception_handler(InvalidTitleError)
    async def bad_request_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Map validation failures to HTTP 400 responses.

        :param _request: Incoming HTTP request.
        :param exc: Raised domain exception.
        :returns: JSON error response.
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'detail': str(exc)},
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def conflict_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Map duplicate user errors to HTTP 409 responses.

        :param _request: Incoming HTTP request.
        :param exc: Raised domain exception.
        :returns: JSON error response.
        """
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={'detail': str(exc)},
        )
