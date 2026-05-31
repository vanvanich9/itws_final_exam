from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
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
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'
