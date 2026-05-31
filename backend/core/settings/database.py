from pydantic_settings import BaseSettings
from pydantic import Field


class DatabaseSettings(BaseSettings):
    host: str = Field(validation_alias='DATABASE_HOST')
    port: int = Field(validation_alias='DATABASE_PORT')
    username: str = Field(validation_alias='DATABASE_USERNAME')
    password: str = Field(validation_alias='DATABASE_PASSWORD')
    database: str = Field(validation_alias='DATABASE_NAME')

    @property
    def url(self) -> str:
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'
