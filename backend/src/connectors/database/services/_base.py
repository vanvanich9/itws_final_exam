"""Base async database connector."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class BaseDatabaseConnector:
    """Async PostgreSQL connector with session management."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
    ) -> None:
        """
        Initialize database engine and session factory.

        :param host: Database host.
        :param port: Database port.
        :param username: Database username.
        :param password: Database password.
        :param database: Database name.
        """
        url = (
            f'postgresql+asyncpg://{username}:{password}'
            f'@{host}:{port}/{database}'
        )
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        """
        Return the async SQLAlchemy engine.

        :returns: Async engine instance.
        """
        return self._engine

    async def close(self) -> None:
        """Dispose of the database engine."""
        await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Provide a transactional async session.

        :yields: Active database session.
        """
        async with self._session_factory() as sess:
            try:
                yield sess
                await sess.commit()
            except Exception:
                await sess.rollback()
                raise
