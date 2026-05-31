from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core.settings.database import DatabaseSettings
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class BaseDatabaseConnector:
    def __init__(
        self, settings: DatabaseSettings | None = None, url: str | None = None
    ) -> None:
        resolved = url
        if resolved is None:
            resolved = (
                settings.url
                if settings is not None
                else DatabaseSettings().url
            )
        self._engine: AsyncEngine = create_async_engine(resolved)
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def close(self) -> None:
        await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as sess:
            try:
                yield sess
                await sess.commit()
            except Exception:
                await sess.rollback()
                raise
