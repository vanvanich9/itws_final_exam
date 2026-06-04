"""Sequential API integration tests for user endpoints.

These tests run against the live API (and shared database) in order,
telling a single story: registration, authentication, profile access,
updates, and deletion. Shared values are passed between steps through
the module-scoped ``state`` fixture in ``conftest.py``.
"""

import pytest
from tests.utils.constants import (
    MAIN_EMAIL,
    MAIN_NAME,
    MAIN_PASSWORD,
    SUFFIX,
)
from tests.utils.funcs import bearer, create_other_user, refresh_cookie


@pytest.mark.order(1)
async def test_register_invalid_email_format(api_client):
    """
    Step 1: registration fails for a malformed email.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/register',
        json={
            'email': 'not-an-email',
            'password': MAIN_PASSWORD,
            'name': MAIN_NAME,
        },
    )

    assert response.status_code == 400


@pytest.mark.order(2)
async def test_register_password_too_short(api_client):
    """
    Step 2: registration fails for a password shorter than 8 chars.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/register',
        json={
            'email': f'short-{SUFFIX}@example.com',
            'password': 'Aa1@',
            'name': MAIN_NAME,
        },
    )

    assert response.status_code == 400


@pytest.mark.order(3)
async def test_register_password_too_long(api_client):
    """
    Step 3: registration fails for a password longer than 20 chars.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/register',
        json={
            'email': f'long-{SUFFIX}@example.com',
            'password': 'Aa1@' + 'a' * 20,
            'name': MAIN_NAME,
        },
    )

    assert response.status_code == 400


@pytest.mark.order(4)
async def test_register_password_no_lowercase(api_client):
    """
    Step 4: registration fails for a password without lowercase letters.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/register',
        json={
            'email': f'nolower-{SUFFIX}@example.com',
            'password': 'SECRET@123',
            'name': MAIN_NAME,
        },
    )

    assert response.status_code == 400


@pytest.mark.order(5)
async def test_register_password_no_uppercase(api_client):
    """
    Step 5: registration fails for a password without uppercase letters.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/register',
        json={
            'email': f'noupper-{SUFFIX}@example.com',
            'password': 'secret@123',
            'name': MAIN_NAME,
        },
    )

    assert response.status_code == 400


@pytest.mark.order(6)
async def test_register_password_no_digit(api_client):
    """
    Step 6: registration fails for a password without digits.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/register',
        json={
            'email': f'nodigit-{SUFFIX}@example.com',
            'password': 'Secret@abc',
            'name': MAIN_NAME,
        },
    )

    assert response.status_code == 400


@pytest.mark.order(7)
async def test_register_password_no_special(api_client):
    """
    Step 7: registration fails for a password without special chars.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/register',
        json={
            'email': f'nospecial-{SUFFIX}@example.com',
            'password': 'Secret1234',
            'name': MAIN_NAME,
        },
    )

    assert response.status_code == 400


@pytest.mark.order(8)
async def test_register_success(api_client, state):
    """
    Step 8: registration succeeds for valid credentials.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.post(
        '/api/users/register',
        json={
            'email': MAIN_EMAIL,
            'password': MAIN_PASSWORD,
            'name': MAIN_NAME,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body['email'] == MAIN_EMAIL
    assert body['name'] == MAIN_NAME
    assert 'created_at' in body
    assert 'updated_at' in body
    state['user_id'] = body['id']


@pytest.mark.order(9)
async def test_login_wrong_email(api_client):
    """
    Step 9: login fails for an unknown email.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/login',
        json={
            'email': f'missing-{SUFFIX}@example.com',
            'password': MAIN_PASSWORD,
        },
    )

    assert response.status_code == 401


@pytest.mark.order(10)
async def test_login_wrong_password(api_client):
    """
    Step 10: login fails for a wrong password.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post(
        '/api/users/login',
        json={'email': MAIN_EMAIL, 'password': 'Wrong@123'},
    )

    assert response.status_code == 401


@pytest.mark.order(11)
async def test_login_success(api_client, state):
    """
    Step 11: login succeeds and issues tokens.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.post(
        '/api/users/login',
        json={'email': MAIN_EMAIL, 'password': MAIN_PASSWORD},
    )

    assert response.status_code == 200
    token = response.json()['token']
    assert token
    refresh = refresh_cookie(response)
    assert refresh is not None
    state['access_token'] = token
    state['refresh_token'] = refresh


@pytest.mark.order(12)
async def test_logout_with_cookie(api_client, state):
    """
    Step 12: logout succeeds when the refresh cookie is present.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    api_client.cookies.set('refresh_token', state['refresh_token'])
    response = await api_client.post('/api/users/logout')
    api_client.cookies.delete('refresh_token')

    assert response.status_code == 200
    assert response.json() == {'success': True}


@pytest.mark.order(13)
async def test_logout_without_cookie(api_client):
    """
    Step 13: logout succeeds even without a refresh cookie.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.post('/api/users/logout')

    assert response.status_code == 200
    assert response.json() == {'success': True}


@pytest.mark.order(14)
async def test_refresh_token(api_client, state):
    """
    Step 14: refresh issues a new token from the refresh cookie.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    api_client.cookies.set('refresh_token', state['refresh_token'])
    response = await api_client.post('/api/users/refresh')
    api_client.cookies.delete('refresh_token')

    assert response.status_code == 200
    token = response.json()['token']
    assert token
    state['access_token'] = token
    rotated = refresh_cookie(response)
    if rotated is not None:
        state['refresh_token'] = rotated


@pytest.mark.order(15)
async def test_get_user_without_bearer(api_client, state):
    """
    Step 15: fetching a profile without a bearer token is rejected.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.get(f'/api/users/{state["user_id"]}')

    assert response.status_code == 401


@pytest.mark.order(16)
async def test_get_me(api_client, state):
    """
    Step 16: the current user is returned via /me.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.get(
        '/api/users/me',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    body = response.json()
    assert body['id'] == state['user_id']
    assert body['email'] == MAIN_EMAIL


@pytest.mark.order(17)
async def test_get_own_user_by_id(api_client, state):
    """
    Step 17: the user can fetch their own profile by id.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.get(
        f'/api/users/{state["user_id"]}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    assert response.json()['id'] == state['user_id']


@pytest.mark.order(18)
async def test_get_other_user_by_id(api_client, state, user_connector):
    """
    Step 18: any authenticated user can fetch another user's profile.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    :param user_connector: User database connector.
    """
    other = await create_other_user(user_connector)

    response = await api_client.get(
        f'/api/users/{other.id}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    assert response.json()['id'] == str(other.id)


@pytest.mark.order(19)
async def test_update_without_bearer(api_client, state):
    """
    Step 19: updating a profile without a bearer token is rejected.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.put(
        f'/api/users/{state["user_id"]}',
        json={'name': 'Should Not Apply'},
    )

    assert response.status_code == 401


@pytest.mark.order(20)
async def test_update_own_user(api_client, state):
    """
    Step 20: the user can update their own profile data.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.put(
        f'/api/users/{state["user_id"]}',
        json={'name': 'Updated Name'},
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    assert response.json()['name'] == 'Updated Name'


@pytest.mark.order(21)
async def test_update_other_user_forbidden(api_client, state, user_connector):
    """
    Step 21: updating another user's profile is forbidden.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    :param user_connector: User database connector.
    """
    other = await create_other_user(user_connector)

    response = await api_client.put(
        f'/api/users/{other.id}',
        json={'name': 'Hacked'},
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 403


@pytest.mark.order(22)
async def test_delete_other_user_without_bearer(api_client, user_connector):
    """
    Step 22: deleting another user without a bearer token is rejected.

    :param api_client: HTTP client fixture.
    :param user_connector: User database connector.
    """
    other = await create_other_user(user_connector)

    response = await api_client.delete(f'/api/users/{other.id}')

    assert response.status_code == 401


@pytest.mark.order(23)
async def test_delete_other_user_forbidden(api_client, state, user_connector):
    """
    Step 23: deleting another user with own bearer token is forbidden.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    :param user_connector: User database connector.
    """
    other = await create_other_user(user_connector)

    response = await api_client.delete(
        f'/api/users/{other.id}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 403


@pytest.mark.order(24)
async def test_delete_own_user(api_client, state):
    """
    Step 24: the user can delete their own profile.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.delete(
        f'/api/users/{state["user_id"]}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    body = response.json()
    assert body['id'] == state['user_id'], f'{body}'
    assert body['email'] == MAIN_EMAIL


@pytest.mark.order(25)
async def test_get_me_with_erroneous_bearer(api_client, state):
    """
    Step 25: /me reports user not found for a stale bearer token.

    The previous step deleted the account, so the still-structurally
    valid access token no longer maps to an existing user, and the API
    answers that the user cannot be found.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.get(
        '/api/users/me',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'user not found'
