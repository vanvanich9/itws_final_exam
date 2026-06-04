"""General application settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class GeneralSettings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    debug: bool = Field(validation_alias='DEBUG', default=False)
    secret_key: str = Field(validation_alias='SECRET_KEY')
