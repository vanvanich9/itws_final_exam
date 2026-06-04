"""User service for Task Manager registration and account operations."""

from uuid import UUID

from core.config.enums import TokenType
from core.settings.general import GeneralSettings
from src.connectors.database.models import User
from src.connectors.database.services.users import UserDatabaseConnector
from src.logic.auth import (
    hash_password,
    is_valid_email,
    is_valid_password,
    issue_tokens,
    validate_token,
    verify_password,
)
from src.logic.models import TokenPair
from src.services.users.errors import (
    InvalidEmailError,
    InvalidPasswordError,
    PasswordMismatchError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


class UserService:
    """User service."""

    def __init__(
        self,
        user_database: UserDatabaseConnector,
        settings: GeneralSettings,
    ):
        """
        Initialize the user service.

        :param user_database: User database connector.
        :param settings: Application settings.
        """
        self.user_database = user_database
        self.settings = settings

    async def authenticate(self, email: str, password: str) -> TokenPair:
        """
        Authenticate a user by email and password.

        :param email: User email.
        :param password: Plain-text password.
        :returns: Issued access and refresh tokens.
        :raises UserNotFoundError: When no user exists for the email.
        :raises PasswordMismatchError: When the password does not match.
        """
        user = await self.user_database.get_by_email(email)
        if user is None:
            raise UserNotFoundError
        if not verify_password(password, user.password):
            raise PasswordMismatchError
        return issue_tokens(user.id, self.settings.secret_key)

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """
        Reissue access and refresh JWT tokens using a valid refresh token.

        :param refresh_token: Valid refresh JWT.
        :returns: New access and refresh token pair.
        :raises ExpiredTokenError: When the refresh token has expired.
        :raises InvalidTokenTypeError: When the token is not a refresh token.
        :raises InvalidTokenError: When the refresh token is malformed.
        """
        payload = validate_token(
            refresh_token,
            self.settings.secret_key,
            token_type=TokenType.REFRESH,
        )
        return issue_tokens(payload.user_id, self.settings.secret_key)

    async def get_by_id(self, user_id: UUID) -> User:
        """
        Fetch a user by identifier.

        :param user_id: User identifier.
        :returns: User instance.
        :raises UserNotFoundError: When the user does not exist.
        """
        user = await self.user_database.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError
        return user

    async def create(self, email: str, password: str, name: str) -> User:
        """
        Create a new user.

        :param email: User email.
        :param password: Plain-text password.
        :param name: Display name.
        :returns: Created user.
        :raises InvalidEmailError: When email format is invalid.
        :raises InvalidPasswordError: When password strength rules fail.
        :raises UserAlreadyExistsError: When the email is already taken.
        """
        if not is_valid_email(email):
            raise InvalidEmailError
        if not is_valid_password(password):
            raise InvalidPasswordError
        if await self.user_database.get_by_email(email) is not None:
            raise UserAlreadyExistsError
        return await self.user_database.create(
            email=email,
            password=hash_password(password),
            name=name,
        )

    async def update(
        self,
        user_id: UUID,
        email: str | None = None,
        password: str | None = None,
        name: str | None = None,
    ) -> User:
        """
        Update a user.

        :param user_id: User identifier.
        :param email: New email, if provided.
        :param password: New plain-text password, if provided.
        :param name: New display name, if provided.
        :returns: Updated user.
        :raises UserNotFoundError: When the user does not exist.
        :raises InvalidEmailError: When email format is invalid.
        :raises InvalidPasswordError: When password strength rules fail.
        """
        if email is not None and not is_valid_email(email):
            raise InvalidEmailError
        if password is not None and not is_valid_password(password):
            raise InvalidPasswordError
        user = await self.get_by_id(user_id)
        return await self.user_database.update(
            user=user,
            email=email,
            password=hash_password(password) if password is not None else None,
            name=name,
        )

    async def delete(self, user_id: UUID) -> User:
        """
        Delete a user.

        :param user_id: User identifier.
        :returns: Deleted user.
        :raises UserNotFoundError: When the user does not exist.
        """
        user = await self.get_by_id(user_id)
        return await self.user_database.delete(user)
