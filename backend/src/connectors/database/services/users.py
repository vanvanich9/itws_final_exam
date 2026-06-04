"""User database connector."""

from uuid import UUID

from sqlalchemy import select
from src.connectors.database.models import User
from src.connectors.database.services._base import BaseDatabaseConnector


class UserDatabaseConnector(BaseDatabaseConnector):
    """CRUD and authentication operations for users."""

    async def create(self, email: str, password: str, name: str) -> User:
        """
        Create a new user.

        :param email: User email.
        :param password: Bcrypt password hash.
        :param name: Display name.
        :returns: Created user.
        """
        async with self.session() as sess:
            user = User(
                email=email,
                password=password,
                name=name,
            )
            sess.add(user)
            await sess.flush()
            return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Fetch a user by identifier.

        :param user_id: User identifier.
        :returns: User if found, otherwise None.
        """
        async with self.session() as sess:
            return await sess.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """
        Fetch a user by email.

        :param email: User email.
        :returns: User if found, otherwise None.
        """
        async with self.session() as sess:
            stmt = select(User).where(User.email == email)
            result = await sess.execute(stmt)
            return result.scalar_one_or_none()

    async def update(
        self,
        user: User,
        email: str | None = None,
        password: str | None = None,
        name: str | None = None,
    ) -> User | None:
        """
        Update user fields.

        :param user: User instance to update.
        :param email: New email, if provided.
        :param password: New password hash, if provided.
        :param name: New display name, if provided.
        :returns: Updated user if found, otherwise None.
        """
        async with self.session() as sess:
            merged = await sess.merge(user)
            if email is not None:
                merged.email = email
            if name is not None:
                merged.name = name
            if password is not None:
                merged.password = password
            await sess.flush()
            return merged

    async def delete(self, user: User) -> User:
        """
        Delete a user.

        :param user: User instance to delete.
        :returns: Deleted user.
        """
        async with self.session() as sess:
            merged = await sess.merge(user)
            await sess.delete(merged)
            await sess.commit()
            return merged
