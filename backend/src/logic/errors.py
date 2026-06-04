"""Logic layer exceptions."""


class InvalidTokenError(Exception):
    """Raised when a JWT is malformed or cannot be verified."""

    def __init__(self, message: str = 'Invalid token') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)


class ExpiredTokenError(InvalidTokenError):
    """Raised when a JWT has expired."""

    def __init__(self, message: str = 'Token expired') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)


class InvalidTokenTypeError(InvalidTokenError):
    """Raised when a JWT has an unexpected type claim."""

    def __init__(self, message: str = 'Invalid token type') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)
