from pydantic import Field
from pydantic_settings import BaseSettings


class GeneralSettings(BaseSettings):
    debug: bool = Field(validation_alias='DEBUG', default=False)
