"""API tests for user endpoints using the ASGI transport."""

import uuid

from src.logic.auth import create_access_token
from src.logic.models import TokenPair
from src.services.users.errors import (
    InvalidEmailError,
    PasswordMismatchError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


async def test_register_returns_created_user(
    client,
    user_service_mock,
    make_user,
):
    """
    Verify registration returns the created user with timestamps.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    :param make_user: User factory fixture.
    """
    user = make_user(email='new@example.com', name='New User')
    user_service_mock.create.return_value = user

    response = await client.post(
        '/api/users/register',
        json={
            'email': 'new@example.com',
            'password': 'Secret@123',
            'name': 'New User',
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body['id'] == str(user.id)
    assert body['email'] == 'new@example.com'
    assert body['name'] == 'New User'
    assert 'created_at' in body
    assert 'updated_at' in body
    user_service_mock.create.assert_awaited_once_with(
        'new@example.com',
        'Secret@123',
        'New User',
    )


async def test_register_conflict_returns_409(client, user_service_mock):
    """
    Verify duplicate registration maps to HTTP 409.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    """
    user_service_mock.create.side_effect = UserAlreadyExistsError()

    response = await client.post(
        '/api/users/register',
        json={
            'email': 'dupe@example.com',
            'password': 'Secret@123',
            'name': 'Dupe',
        },
    )

    assert response.status_code == 409


async def test_register_invalid_email_returns_400(client, user_service_mock):
    """
    Verify invalid email registration maps to HTTP 400.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    """
    user_service_mock.create.side_effect = InvalidEmailError()

    response = await client.post(
        '/api/users/register',
        json={
            'email': 'bad-email',
            'password': 'Secret@123',
            'name': 'Bad',
        },
    )

    assert response.status_code == 400


async def test_login_returns_token_and_cookie(client, user_service_mock):
    """
    Verify login returns an access token and sets the refresh cookie.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    """
    user_service_mock.authenticate.return_value = TokenPair(
        access_token='access-jwt',
        refresh_token='refresh-jwt',
    )

    response = await client.post(
        '/api/users/login',
        json={'email': 'user@example.com', 'password': 'Secret@123'},
    )

    assert response.status_code == 200
    assert response.json() == {'token': 'access-jwt'}
    assert response.cookies.get('refresh_token') == 'refresh-jwt'


async def test_login_bad_credentials_returns_401(client, user_service_mock):
    """
    Verify failed login maps to HTTP 401.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    """
    user_service_mock.authenticate.side_effect = PasswordMismatchError()

    response = await client.post(
        '/api/users/login',
        json={'email': 'user@example.com', 'password': 'Wrong@123'},
    )

    assert response.status_code == 401


async def test_refresh_rotates_tokens(client, user_service_mock):
    """
    Verify refresh issues a new token using the refresh cookie.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    """
    user_service_mock.refresh_tokens.return_value = TokenPair(
        access_token='access-2',
        refresh_token='refresh-2',
    )

    client.cookies.set('refresh_token', 'old-refresh')
    response = await client.post('/api/users/refresh')
    client.cookies.delete('refresh_token')

    assert response.status_code == 200
    assert response.json() == {'token': 'access-2'}
    assert response.cookies.get('refresh_token') == 'refresh-2'
    user_service_mock.refresh_tokens.assert_called_once_with('old-refresh')


async def test_refresh_without_cookie_returns_401(client):
    """
    Verify refresh without a cookie maps to HTTP 401.

    :param client: HTTP client fixture.
    """
    response = await client.post('/api/users/refresh')

    assert response.status_code == 401


async def test_logout_clears_cookie(client):
    """
    Verify logout clears the refresh cookie and reports success.

    :param client: HTTP client fixture.
    """
    response = await client.post('/api/users/logout')

    assert response.status_code == 200
    assert response.json() == {'success': True}
    set_cookie = '; '.join(response.headers.get_list('set-cookie'))
    assert 'refresh_token=' in set_cookie


async def test_get_user_by_id_authorized(
    client,
    user_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify an authenticated user can view another user's profile.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())
    target = make_user(email='target@example.com', name='Target')
    user_service_mock.get_by_id.return_value = target

    response = await client.get(f'/api/users/{target.id}')

    assert response.status_code == 200
    body = response.json()
    assert body['id'] == str(target.id)
    assert body['email'] == 'target@example.com'


async def test_get_user_by_id_with_real_token(
    client,
    user_service_mock,
    make_user,
    secret_key,
):
    """
    Verify the real auth dependency resolves a bearer access token.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    :param make_user: User factory fixture.
    :param secret_key: Signing secret fixture.
    """
    user = make_user()
    user_service_mock.get_by_id.return_value = user
    token = create_access_token(user.id, secret_key)

    response = await client.get(
        f'/api/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200
    assert response.json()['id'] == str(user.id)


async def test_get_user_by_id_requires_auth(client, make_user):
    """
    Verify viewing a profile without credentials maps to HTTP 401.

    :param client: HTTP client fixture.
    :param make_user: User factory fixture.
    """
    response = await client.get(f'/api/users/{make_user().id}')

    assert response.status_code == 401


async def test_get_user_by_id_not_found(
    client,
    user_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify a missing user surfaces the not-found error mapping.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())
    user_service_mock.get_by_id.side_effect = UserNotFoundError()

    response = await client.get(f'/api/users/{uuid.uuid4()}')

    assert response.status_code == 401


async def test_update_user_self(
    client,
    user_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify a user can update their own profile.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    user = make_user()
    authenticate_as(user)
    updated = make_user(
        user_id=user.id,
        email='updated@example.com',
        name='Updated',
    )
    user_service_mock.update.return_value = updated

    response = await client.put(
        f'/api/users/{user.id}',
        json={'email': 'updated@example.com', 'name': 'Updated'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['email'] == 'updated@example.com'
    assert body['name'] == 'Updated'
    user_service_mock.update.assert_awaited_once_with(
        user.id,
        email='updated@example.com',
        password=None,
        name='Updated',
    )


async def test_update_user_other_forbidden(
    client,
    user_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify updating another user's profile is forbidden.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())

    response = await client.put(
        f'/api/users/{uuid.uuid4()}',
        json={'name': 'Hacker'},
    )

    assert response.status_code == 403
    user_service_mock.update.assert_not_awaited()


async def test_delete_user_self(
    client,
    user_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify a user can delete their own profile.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    user = make_user()
    authenticate_as(user)
    user_service_mock.delete.return_value = user

    response = await client.delete(f'/api/users/{user.id}')

    assert response.status_code == 200
    body = response.json()
    assert body['id'] == str(user.id)
    assert body['email'] == user.email
    user_service_mock.delete.assert_awaited_once_with(user.id)


async def test_delete_user_other_forbidden(
    client,
    user_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify deleting another user's profile is forbidden.

    :param client: HTTP client fixture.
    :param user_service_mock: Mock user service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())

    response = await client.delete(f'/api/users/{uuid.uuid4()}')

    assert response.status_code == 403
    user_service_mock.delete.assert_not_awaited()
