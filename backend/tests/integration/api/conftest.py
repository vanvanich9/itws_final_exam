"""Fixtures for API integration tests."""

import httpx
import pytest
from tests.settings import ApiTestSettings


@pytest.fixture(scope='module')
def state() -> dict:
    """
    Hold values shared across sequential API test steps.

    :returns: Mutable shared-state mapping.
    """
    return {}


@pytest.fixture
def test_settings() -> ApiTestSettings:
    """
    Build API test settings from environment.

    :returns: API test settings instance.
    """
    return ApiTestSettings()


@pytest.fixture
async def api_client(test_settings: ApiTestSettings):
    """
    Provide async HTTP client for API tests.

    :param test_settings: API test settings.
    :yields: Configured HTTP client.
    """
    async with httpx.AsyncClient(
        base_url=test_settings.api_url,
        timeout=test_settings.api_timeout,
    ) as client:
        yield client
