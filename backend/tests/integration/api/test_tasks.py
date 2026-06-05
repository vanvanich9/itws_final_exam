"""Sequential API integration tests for task endpoints.

These tests run against the live API (and shared database) in order,
telling a single story for a single task owner: creation, retrieval,
ownership enforcement, search filtering, and deletion. Shared values are
passed between steps through the module-scoped ``state`` fixture in
``conftest.py``.

The owner ends the story with two tasks in the database (one recent, one
backdated and finished) plus one foreign task owned by another user, which
is reused to verify that cross-user access is always rejected.
"""

import uuid

import pytest
from core.config.enums import PriorityTask, StatusTask
from tests.utils.constants import (
    TASK_OWNER_EMAIL,
    TASK_OWNER_NAME,
    TASK_OWNER_PASSWORD,
)
from tests.utils.funcs import age_task, bearer, create_other_user, create_task


@pytest.mark.order(1)
async def test_register_and_login_owner(api_client, state):
    """
    Step 0: register and authenticate the task owner.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    register = await api_client.post(
        '/api/users/register',
        json={
            'email': TASK_OWNER_EMAIL,
            'password': TASK_OWNER_PASSWORD,
            'name': TASK_OWNER_NAME,
        },
    )
    assert register.status_code == 201
    state['user_id'] = register.json()['id']

    login = await api_client.post(
        '/api/users/login',
        json={'email': TASK_OWNER_EMAIL, 'password': TASK_OWNER_PASSWORD},
    )
    assert login.status_code == 200
    state['access_token'] = login.json()['token']


@pytest.mark.order(2)
async def test_create_task_without_title_fails(api_client, state):
    """
    Step 1: creating a task with an empty title is rejected.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.post(
        '/api/tasks',
        json={'title': '   ', 'description': 'No real title'},
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 400


@pytest.mark.order(3)
async def test_create_task(api_client, state):
    """
    Step 2: the owner creates a task and receives the full model.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.post(
        '/api/tasks',
        json={
            'title': 'Owner task',
            'description': 'First task',
            'priority': PriorityTask.MEDIUM,
        },
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 201
    body = response.json()
    assert body['title'] == 'Owner task'
    assert body['user_id'] == state['user_id']
    assert 'created_at' in body
    assert 'updated_at' in body
    state['task_id'] = body['id']


@pytest.mark.order(4)
async def test_get_own_task(api_client, state):
    """
    Step 3: the owner fetches their own task by identifier.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.get(
        f'/api/tasks/{state["task_id"]}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    assert response.json()['id'] == state['task_id']


@pytest.mark.order(5)
async def test_get_other_task_forbidden(
    api_client,
    state,
    user_connector,
    task_connector,
):
    """
    Step 4: fetching another user's task is forbidden.

    A foreign user and task are prepared directly in the database and
    reused by later ownership checks.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    :param user_connector: User database connector.
    :param task_connector: Task database connector.
    """
    other = await create_other_user(user_connector)
    foreign = await create_task(
        task_connector,
        other.id,
        title='Foreign task',
    )
    state['foreign_task_id'] = str(foreign.id)

    response = await api_client.get(
        f'/api/tasks/{state["foreign_task_id"]}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 403


@pytest.mark.order(6)
async def test_update_own_task(api_client, state):
    """
    Step 5: the owner updates their own task.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.put(
        f'/api/tasks/{state["task_id"]}',
        json={'title': 'Owner task updated', 'status': StatusTask.IN_PROGRESS},
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    body = response.json()
    assert body['title'] == 'Owner task updated'
    assert body['status'] == StatusTask.IN_PROGRESS


@pytest.mark.order(7)
async def test_update_other_task_forbidden(api_client, state):
    """
    Step 6: updating another user's task is forbidden.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.put(
        f'/api/tasks/{state["foreign_task_id"]}',
        json={'title': 'Hacked'},
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 403


@pytest.mark.order(8)
async def test_search_finished_within_weeks_zero(
    api_client,
    state,
    task_connector,
):
    """
    Step 7: search with finished_within_weeks=0 returns all own tasks.

    A second owned task is created and backdated by two weeks with a
    finished status, giving the owner two tasks total. With the filter
    disabled (0) both are returned.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    :param task_connector: Task database connector.
    """
    aged = await create_task(
        task_connector,
        uuid.UUID(state['user_id']),
        title='Old finished task',
        status=StatusTask.DONE,
    )
    aged = await age_task(task_connector, aged, weeks=2)
    state['aged_task_id'] = str(aged.id)

    response = await api_client.post(
        '/api/tasks/search',
        json={'finished_within_weeks': 0},
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    body = response.json()
    assert body['count'] == 2
    assert body['finished_within_weeks'] == 0
    returned_ids = {task['id'] for task in body['tasks']}
    assert returned_ids == {state['task_id'], state['aged_task_id']}


@pytest.mark.order(9)
async def test_search_finished_within_weeks_one(api_client, state):
    """
    Step 8: search with finished_within_weeks=1 excludes stale finished tasks.

    The backdated finished task falls outside the one-week window, so only
    the recent task remains.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.post(
        '/api/tasks/search',
        json={'finished_within_weeks': 1},
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    body = response.json()
    assert body['count'] == 1
    assert body['finished_within_weeks'] == 1
    assert body['tasks'][0]['id'] == state['task_id']


@pytest.mark.order(10)
async def test_delete_other_task_forbidden(api_client, state):
    """
    Step 9: deleting another user's task is forbidden.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.delete(
        f'/api/tasks/{state["foreign_task_id"]}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 403


@pytest.mark.order(11)
async def test_delete_own_task(api_client, state):
    """
    Step 10: the owner deletes their own task.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.delete(
        f'/api/tasks/{state["task_id"]}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 200
    assert response.json()['id'] == state['task_id']


@pytest.mark.order(12)
async def test_get_deleted_task_returns_404(api_client, state):
    """
    Step 11: fetching the deleted task by its identifier returns 404.

    :param api_client: HTTP client fixture.
    :param state: Shared sequential state.
    """
    response = await api_client.get(
        f'/api/tasks/{state["task_id"]}',
        headers=bearer(state['access_token']),
    )

    assert response.status_code == 404
