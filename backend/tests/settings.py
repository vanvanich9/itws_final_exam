from pydantic import Field
from pydantic_settings import BaseSettings


class ApiTestSettings(BaseSettings):
    api_base_url: str = Field(
        default='http://localhost:8000',
        validation_alias='API_BASE_URL',
    )
    api_timeout: float = Field(default=5.0, validation_alias='API_TIMEOUT')

    @property
    def api_url(self) -> str:
        return self.api_base_url.rstrip('/')
