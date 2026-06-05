"""API tests for task endpoints using the ASGI transport."""

import uuid

from core.config.enums import PriorityTask, StatusTask, TypeTask
from src.services.tasks.errors import InvalidTitleError, TaskNotFoundError


async def test_search_tasks(
    client,
    task_service_mock,
    make_user,
    make_task,
    authenticate_as,
):
    """
    Verify search returns tasks for the authenticated user only.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param make_task: Task factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    user = make_user()
    authenticate_as(user)
    task = make_task(user_id=user.id)
    task_service_mock.list.return_value = [task]

    response = await client.post(
        '/api/tasks/search',
        json={
            'statuses': [StatusTask.BACKLOG],
            'finished_within_weeks': 0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['count'] == 1
    assert body['finished_within_weeks'] == 0
    assert body['tasks'][0]['id'] == str(task.id)
    assert body['tasks'][0]['user_id'] == str(user.id)
    task_service_mock.list.assert_awaited_once_with(
        user_id=user.id,
        statuses=[StatusTask.BACKLOG],
        priorities=None,
        task_types=None,
        finished_within_weeks=None,
    )


async def test_search_tasks_applies_finished_within_weeks(
    client,
    task_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify a non-zero finished_within_weeks filter is forwarded.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    user = make_user()
    authenticate_as(user)
    task_service_mock.list.return_value = []

    response = await client.post(
        '/api/tasks/search',
        json={'finished_within_weeks': 2},
    )

    assert response.status_code == 200
    assert response.json()['finished_within_weeks'] == 2
    task_service_mock.list.assert_awaited_once_with(
        user_id=user.id,
        statuses=None,
        priorities=None,
        task_types=None,
        finished_within_weeks=2,
    )


async def test_search_tasks_requires_auth(client):
    """
    Verify search without credentials maps to HTTP 401.

    :param client: HTTP client fixture.
    """
    response = await client.post('/api/tasks/search', json={})

    assert response.status_code == 401


async def test_create_task(
    client,
    task_service_mock,
    make_user,
    make_task,
    authenticate_as,
):
    """
    Verify task creation returns the full task model.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param make_task: Task factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    user = make_user()
    authenticate_as(user)
    created = make_task(user_id=user.id, title='New task')
    task_service_mock.create.return_value = created

    response = await client.post(
        '/api/tasks',
        json={'title': 'New task', 'description': 'Details'},
    )

    assert response.status_code == 201
    body = response.json()
    assert body['id'] == str(created.id)
    assert body['title'] == 'New task'
    assert body['task_type'] == TypeTask.OTHER
    assert 'created_at' in body
    assert 'updated_at' in body
    task_service_mock.create.assert_awaited_once_with(
        user_id=user.id,
        title='New task',
        description='Details',
        status=StatusTask.BACKLOG,
        priority=PriorityTask.LOW,
        task_type=TypeTask.OTHER,
        pull_request_url=None,
    )


async def test_create_task_invalid_title(
    client,
    task_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify invalid title creation maps to HTTP 400.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())
    task_service_mock.create.side_effect = InvalidTitleError()

    response = await client.post('/api/tasks', json={'title': '   '})

    assert response.status_code == 400
    task_service_mock.create.assert_awaited_once()


async def test_get_task(
    client,
    task_service_mock,
    make_user,
    make_task,
    authenticate_as,
):
    """
    Verify the owner can fetch a task by identifier.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param make_task: Task factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    user = make_user()
    task = make_task(user_id=user.id)
    authenticate_as(user)
    task_service_mock.get_by_id.return_value = task

    response = await client.get(f'/api/tasks/{task.id}')

    assert response.status_code == 200
    assert response.json()['id'] == str(task.id)


async def test_get_task_other_user_forbidden(
    client,
    task_service_mock,
    make_user,
    make_task,
    authenticate_as,
):
    """
    Verify fetching another user's task is forbidden.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param make_task: Task factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())
    task_service_mock.get_by_id.return_value = make_task()

    response = await client.get(f'/api/tasks/{uuid.uuid4()}')

    assert response.status_code == 403


async def test_get_task_not_found(
    client,
    task_service_mock,
    make_user,
    authenticate_as,
):
    """
    Verify a missing task maps to HTTP 404.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())
    task_service_mock.get_by_id.side_effect = TaskNotFoundError()

    response = await client.get(f'/api/tasks/{uuid.uuid4()}')

    assert response.status_code == 404


async def test_update_task(
    client,
    task_service_mock,
    make_user,
    make_task,
    authenticate_as,
):
    """
    Verify the owner can update a task.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param make_task: Task factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    user = make_user()
    task = make_task(user_id=user.id)
    updated = make_task(
        task_id=task.id,
        user_id=user.id,
        title='Updated',
        status=StatusTask.DONE,
    )
    authenticate_as(user)
    task_service_mock.get_by_id.return_value = task
    task_service_mock.update.return_value = updated

    response = await client.put(
        f'/api/tasks/{task.id}',
        json={'title': 'Updated', 'status': StatusTask.DONE},
    )

    assert response.status_code == 200
    assert response.json()['title'] == 'Updated'
    task_service_mock.update.assert_awaited_once_with(
        task.id,
        title='Updated',
        description=None,
        status=StatusTask.DONE,
        priority=None,
        task_type=None,
        pull_request_url=None,
    )


async def test_update_task_other_user_forbidden(
    client,
    task_service_mock,
    make_user,
    make_task,
    authenticate_as,
):
    """
    Verify updating another user's task is forbidden.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param make_task: Task factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())
    task_service_mock.get_by_id.return_value = make_task()

    response = await client.put(
        f'/api/tasks/{uuid.uuid4()}',
        json={'title': 'Hacker'},
    )

    assert response.status_code == 403
    task_service_mock.update.assert_not_awaited()


async def test_delete_task(
    client,
    task_service_mock,
    make_user,
    make_task,
    authenticate_as,
):
    """
    Verify the owner can delete a task.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param make_task: Task factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    user = make_user()
    task = make_task(user_id=user.id)
    authenticate_as(user)
    task_service_mock.get_by_id.return_value = task
    task_service_mock.delete.return_value = task

    response = await client.delete(f'/api/tasks/{task.id}')

    assert response.status_code == 200
    assert response.json()['id'] == str(task.id)
    task_service_mock.delete.assert_awaited_once_with(task.id)


async def test_delete_task_other_user_forbidden(
    client,
    task_service_mock,
    make_user,
    make_task,
    authenticate_as,
):
    """
    Verify deleting another user's task is forbidden.

    :param client: HTTP client fixture.
    :param task_service_mock: Mock task service.
    :param make_user: User factory fixture.
    :param make_task: Task factory fixture.
    :param authenticate_as: Authentication override helper.
    """
    authenticate_as(make_user())
    task_service_mock.get_by_id.return_value = make_task()

    response = await client.delete(f'/api/tasks/{uuid.uuid4()}')

    assert response.status_code == 403
    task_service_mock.delete.assert_not_awaited()
