"""Database connection settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """PostgreSQL connection settings loaded from environment variables."""

    host: str = Field(default='postgres', validation_alias='DATABASE_HOST')
    port: int = Field(default=5432, validation_alias='DATABASE_PORT')
    username: str = Field(
        default='postgres',
        validation_alias='DATABASE_USERNAME',
    )
    password: str = Field(
        default='postgres',
        validation_alias='DATABASE_PASSWORD',
    )
    database: str = Field(default='db', validation_alias='DATABASE_NAME')

    @property
    def url(self) -> str:
        """
        Build async SQLAlchemy database URL.

        :returns: PostgreSQL connection URL for asyncpg.
        """
        return (
            f'postgresql+asyncpg://{self.username}:{self.password}'
            f'@{self.host}:{self.port}/{self.database}'
        )
