"""Task service exceptions."""


class InvalidTitleError(ValueError):
    """Raised when the task title is missing or empty."""

    def __init__(self, message: str = 'Incorrect title') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)


class TaskNotFoundError(Exception):
    """Raised when a task cannot be found."""

    def __init__(self, message: str = 'task not found') -> None:
        """
        Initialize the exception.

        :param message: Error message.
        """
        super().__init__(message)
