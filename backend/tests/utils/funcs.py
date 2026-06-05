"""Shared test helper functions."""

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import httpx
from core.config.enums import PriorityTask, StatusTask, TypeTask
from fastapi import Response
from src.connectors.database.services.tasks import TaskDatabaseConnector
from src.connectors.database.services.users import UserDatabaseConnector


def set_cookie_header(response: Response) -> str:
    """
    Read the Set-Cookie header from a response.

    :param response: Response carrying the cookie.
    :returns: Set-Cookie header value.
    """
    return response.headers['set-cookie']


def request_with_state(**state) -> SimpleNamespace:
    """
    Build a request-like object exposing app state.

    :param state: Attributes to attach to app state.
    :returns: Request namespace.
    """
    return SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(**state)),
    )


def bearer(token: str) -> dict[str, str]:
    """
    Build an Authorization header for a bearer token.

    :param token: Access token value.
    :returns: Header mapping with the bearer token.
    """
    return {'Authorization': f'Bearer {token}'}


def refresh_cookie(response: httpx.Response) -> str | None:
    """
    Extract the refresh token cookie value from a response.

    :param response: HTTP response carrying the cookie.
    :returns: Refresh token value when present, otherwise None.
    """
    value = response.cookies.get('refresh_token')
    if value:
        return value
    for header in response.headers.get_list('set-cookie'):
        if header.startswith('refresh_token='):
            return header.split('=', 1)[1].split(';', 1)[0]
    return None


async def create_other_user(
    user_connector: UserDatabaseConnector,
) -> object:
    """
    Create a distinct secondary user directly in the database.

    :param user_connector: User database connector.
    :returns: Created user instance.
    """
    suffix = uuid.uuid4().hex[:8]
    return await user_connector.create(
        email=f'other-{suffix}@example.com',
        password='secret',
        name='Other User',
    )


async def create_task(
    task_connector: TaskDatabaseConnector,
    user_id: uuid.UUID,
    title: str = 'Seed task',
    description: str | None = 'Seed description',
    status: StatusTask = StatusTask.BACKLOG,
    priority: PriorityTask = PriorityTask.LOW,
    task_type: TypeTask = TypeTask.OTHER,
) -> object:
    """
    Create a task directly in the database.

    :param task_connector: Task database connector.
    :param user_id: Owner user identifier.
    :param title: Task title.
    :param description: Task description.
    :param status: Task status.
    :param priority: Task priority.
    :param task_type: Task type.
    :returns: Created task instance.
    """
    return await task_connector.create(
        user_id=user_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        task_type=task_type,
    )


async def age_task(
    task_connector: TaskDatabaseConnector,
    task: object,
    weeks: int,
) -> object:
    """
    Backdate a task's created and updated timestamps by some weeks.

    :param task_connector: Task database connector.
    :param task: Task instance to backdate.
    :param weeks: Number of weeks to subtract from the current time.
    :returns: Updated task instance.
    """
    aged = (datetime.now(UTC) - timedelta(weeks=weeks)).replace(tzinfo=None)
    async with task_connector.session() as sess:
        row = await sess.merge(task)
        row.created_at = aged
        row.updated_at = aged
        await sess.flush()
        return row
