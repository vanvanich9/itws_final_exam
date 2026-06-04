"""User service exceptions."""


class InvalidEmailError(ValueError):
    """Raised when the email address format is invalid."""

    def __init__(self, message: str = 'Incorrect email') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)


class InvalidPasswordError(ValueError):
    """Raised when the password does not meet strength requirements."""

    def __init__(self, message: str = 'Incorrect password') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""

    def __init__(self, message: str = 'user not found') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)


class PasswordMismatchError(Exception):
    """Raised when the provided password does not match the stored hash."""

    def __init__(self, message: str = 'incorrect password') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)


class UserAlreadyExistsError(Exception):
    """Raised when a user with the same email already exists."""

    def __init__(self, message: str = 'user already exists') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)
