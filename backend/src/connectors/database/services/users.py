"""User database connector."""

from uuid import UUID

import bcrypt
from sqlalchemy import select
from src.connectors.database.models import User
from src.connectors.database.services._base import BaseDatabaseConnector


class UserDatabaseConnector(BaseDatabaseConnector):
    """CRUD and authentication operations for users."""

    @staticmethod
    def _hash_password(plain: str) -> str:
        """
        Hash a plain-text password.

        :param plain: Plain-text password.
        :returns: Bcrypt password hash.
        """
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def _verify_password(plain: str, hashed: str) -> bool:
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

    async def create(self, email: str, password: str, name: str) -> User:
        """
        Create a new user.

        :param email: User email.
        :param password: Plain-text password.
        :param name: Display name.
        :returns: Created user.
        """
        async with self.session() as sess:
            row = User(
                email=email,
                password=self._hash_password(password),
                name=name,
            )
            sess.add(row)
            await sess.flush()
            await sess.refresh(row)
            return row

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Fetch a user by identifier.

        :param user_id: User identifier.
        :returns: User if found, otherwise None.
        """
        async with self.session() as sess:
            return await sess.get(User, user_id)

    async def authenticate(self, email: str, password: str) -> User | None:
        """
        Authenticate a user by email and password.

        :param email: User email.
        :param password: Plain-text password.
        :returns: User if credentials are valid, otherwise None.
        """
        async with self.session() as sess:
            stmt = select(User).where(User.email == email)
            result = await sess.execute(stmt)
            user = result.scalar_one_or_none()
            if user is None:
                return None
            if not self._verify_password(password, user.password):
                return None
            return user

    async def update(
        self,
        user_id: UUID,
        email: str | None = None,
        password: str | None = None,
        name: str | None = None,
    ) -> User | None:
        """
        Update user fields.

        :param user_id: User identifier.
        :param email: New email, if provided.
        :param password: New plain-text password, if provided.
        :param name: New display name, if provided.
        :returns: Updated user if found, otherwise None.
        """
        async with self.session() as sess:
            row = await sess.get(User, user_id)
            if row is None:
                return None
            if email is not None:
                row.email = email
            if name is not None:
                row.name = name
            if password is not None:
                row.password = self._hash_password(password)
            await sess.flush()
            await sess.refresh(row)
            return row

    async def delete(self, user: User) -> bool:
        """
        Delete a user.

        :param user: User instance to delete.
        :returns: True when deletion succeeds.
        """
        async with self.session() as sess:
            row = await sess.merge(user)
            await sess.delete(row)
            await sess.flush()
            return True
