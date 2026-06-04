"""Settings unit tests."""

import pytest
from core.settings.database import DatabaseSettings
from core.settings.general import GeneralSettings
from tests.settings import ApiTestSettings


def test_api_test_settings_defaults(monkeypatch):
    """
    Verify API test settings defaults without environment variables.

    :param monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.delenv('API_BASE_URL', raising=False)
    monkeypatch.delenv('API_TIMEOUT', raising=False)

    settings = ApiTestSettings()

    assert settings.api_base_url == 'http://localhost:8000'
    assert settings.api_timeout == 5.0
    assert settings.api_url == 'http://localhost:8000'


def test_api_test_settings_from_env(monkeypatch):
    """
    Verify API test settings are loaded from environment.

    :param monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setenv('API_BASE_URL', 'http://api:8000/')
    monkeypatch.setenv('API_TIMEOUT', '10')

    settings = ApiTestSettings()

    assert settings.api_base_url == 'http://api:8000/'
    assert settings.api_timeout == 10.0
    assert settings.api_url == 'http://api:8000'


def test_database_settings_defaults(monkeypatch):
    """
    Verify database settings defaults without environment variables.

    :param monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.delenv('DATABASE_HOST', raising=False)
    monkeypatch.delenv('DATABASE_PORT', raising=False)
    monkeypatch.delenv('DATABASE_USERNAME', raising=False)
    monkeypatch.delenv('DATABASE_PASSWORD', raising=False)
    monkeypatch.delenv('DATABASE_NAME', raising=False)

    settings = DatabaseSettings()

    assert settings.host == 'postgres'
    assert settings.port == 5432
    assert settings.username == 'postgres'
    assert settings.password == 'postgres'
    assert settings.database == 'db'
    assert settings.url == (
        'postgresql+asyncpg://postgres:postgres@postgres:5432/db'
    )


def test_general_settings_debug_default(monkeypatch):
    """
    Verify debug flag defaults to false.

    :param monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.delenv('DEBUG', raising=False)

    settings = GeneralSettings()

    assert settings.debug is False


@pytest.mark.parametrize('raw_value', ['1', 'true', 'True', 'yes'])
def test_general_settings_debug_enabled(monkeypatch, raw_value):
    """
    Verify debug flag is enabled from truthy environment values.

    :param monkeypatch: Pytest monkeypatch fixture.
    :param raw_value: Raw environment value for DEBUG.
    """
    monkeypatch.setenv('DEBUG', raw_value)

    settings = GeneralSettings()

    assert settings.debug is True
