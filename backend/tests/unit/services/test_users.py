"""Unit tests for the user service business logic."""

import uuid
from types import SimpleNamespace

import pytest
from core.config.enums import TokenType
from src.logic.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    validate_token,
)
from src.logic.errors import InvalidTokenTypeError
from src.logic.models import TokenPair
from src.services.users.errors import (
    InvalidEmailError,
    InvalidPasswordError,
    PasswordMismatchError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from tests.utils.constants import VALID_EMAIL, VALID_PASSWORD


async def test_authenticate_success(service, connector, secret_key):
    """
    Verify authentication issues tokens for valid credentials.

    :param service: User service under test.
    :param connector: Mock connector.
    :param secret_key: Signing secret fixture.
    """
    user_id = uuid.uuid4()
    connector.get_by_email.return_value = SimpleNamespace(
        id=user_id,
        password=hash_password(VALID_PASSWORD),
    )

    pair = await service.authenticate(VALID_EMAIL, VALID_PASSWORD)

    assert isinstance(pair, TokenPair)
    payload = validate_token(
        pair.access_token,
        secret_key,
        token_type=TokenType.ACCESS,
    )
    assert payload.user_id == user_id


async def test_authenticate_user_not_found(service, connector):
    """
    Verify authentication fails when the user is missing.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    connector.get_by_email.return_value = None

    with pytest.raises(UserNotFoundError):
        await service.authenticate(VALID_EMAIL, VALID_PASSWORD)


async def test_authenticate_wrong_password(service, connector):
    """
    Verify authentication fails on password mismatch.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    connector.get_by_email.return_value = SimpleNamespace(
        id=uuid.uuid4(),
        password=hash_password('Another@123'),
    )

    with pytest.raises(PasswordMismatchError):
        await service.authenticate(VALID_EMAIL, VALID_PASSWORD)


async def test_create_success(service, connector):
    """
    Verify user creation hashes the password and persists the user.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    connector.get_by_email.return_value = None
    created = SimpleNamespace(id=uuid.uuid4())
    connector.create.return_value = created

    result = await service.create(VALID_EMAIL, VALID_PASSWORD, 'Test User')

    assert result is created
    connector.create.assert_awaited_once()
    kwargs = connector.create.await_args.kwargs
    assert kwargs['email'] == VALID_EMAIL
    assert kwargs['name'] == 'Test User'
    assert kwargs['password'] != VALID_PASSWORD


async def test_create_invalid_email(service, connector):
    """
    Verify creation rejects an invalid email before persisting.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    with pytest.raises(InvalidEmailError):
        await service.create('not-an-email', VALID_PASSWORD, 'Test User')

    connector.create.assert_not_awaited()


async def test_create_invalid_password(service, connector):
    """
    Verify creation rejects a weak password before persisting.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    with pytest.raises(InvalidPasswordError):
        await service.create(VALID_EMAIL, 'weak', 'Test User')

    connector.create.assert_not_awaited()


async def test_create_duplicate_email(service, connector):
    """
    Verify creation rejects an already-registered email.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    connector.get_by_email.return_value = SimpleNamespace(id=uuid.uuid4())

    with pytest.raises(UserAlreadyExistsError):
        await service.create(VALID_EMAIL, VALID_PASSWORD, 'Test User')

    connector.create.assert_not_awaited()


async def test_refresh_tokens_success(service, secret_key):
    """
    Verify refreshing a valid refresh token issues a new pair.

    :param service: User service under test.
    :param secret_key: Signing secret fixture.
    """
    user_id = uuid.uuid4()
    refresh = create_refresh_token(user_id, secret_key)

    pair = service.refresh_tokens(refresh)

    assert isinstance(pair, TokenPair)
    payload = validate_token(
        pair.refresh_token,
        secret_key,
        token_type=TokenType.REFRESH,
    )
    assert payload.user_id == user_id


async def test_refresh_tokens_rejects_access_token(service, secret_key):
    """
    Verify refreshing fails when given an access token.

    :param service: User service under test.
    :param secret_key: Signing secret fixture.
    """
    access = create_access_token(uuid.uuid4(), secret_key)

    with pytest.raises(InvalidTokenTypeError):
        service.refresh_tokens(access)


async def test_get_by_id_success(service, connector):
    """
    Verify fetching an existing user returns it.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    user = SimpleNamespace(id=uuid.uuid4())
    connector.get_by_id.return_value = user

    result = await service.get_by_id(user.id)

    assert result is user


async def test_get_by_id_not_found(service, connector):
    """
    Verify fetching a missing user raises UserNotFoundError.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    connector.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await service.get_by_id(uuid.uuid4())


async def test_update_success(service, connector):
    """
    Verify update validates inputs and delegates to the connector.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    user = SimpleNamespace(id=uuid.uuid4())
    connector.get_by_id.return_value = user
    updated = SimpleNamespace(id=user.id, name='New Name')
    connector.update.return_value = updated

    result = await service.update(
        user.id,
        email='new@example.com',
        password=VALID_PASSWORD,
        name='New Name',
    )

    assert result is updated
    connector.update.assert_awaited_once()
    kwargs = connector.update.await_args.kwargs
    assert kwargs['user'] is user
    assert kwargs['email'] == 'new@example.com'
    assert kwargs['name'] == 'New Name'
    assert kwargs['password'] != VALID_PASSWORD


async def test_update_invalid_email(service, connector):
    """
    Verify update rejects an invalid email.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    with pytest.raises(InvalidEmailError):
        await service.update(uuid.uuid4(), email='bad-email')

    connector.update.assert_not_awaited()


async def test_update_invalid_password(service, connector):
    """
    Verify update rejects a weak password.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    with pytest.raises(InvalidPasswordError):
        await service.update(uuid.uuid4(), password='weak')

    connector.update.assert_not_awaited()


async def test_update_user_not_found(service, connector):
    """
    Verify update raises when the target user does not exist.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    connector.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await service.update(uuid.uuid4(), name='New Name')

    connector.update.assert_not_awaited()


async def test_delete_success(service, connector):
    """
    Verify deletion fetches then removes the user.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    user = SimpleNamespace(id=uuid.uuid4())
    connector.get_by_id.return_value = user
    connector.delete.return_value = user

    result = await service.delete(user.id)

    assert result is user
    connector.delete.assert_awaited_once_with(user)


async def test_delete_user_not_found(service, connector):
    """
    Verify deletion raises when the user is missing.

    :param service: User service under test.
    :param connector: Mock connector.
    """
    connector.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await service.delete(uuid.uuid4())

    connector.delete.assert_not_awaited()
