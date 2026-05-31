from pydantic_settings import BaseSettings
from pydantic import Field


class GeneralSettings(BaseSettings):
    debug: bool = Field(validation_alias='DEBUG', default=False)
