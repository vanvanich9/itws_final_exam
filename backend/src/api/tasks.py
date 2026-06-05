"""Task endpoints."""

from uuid import UUID

from core.config.openapi import (
    AUTH_RESPONSES,
    RESPONSE_400,
    TASK_OWNER_RESPONSES,
)
from fastapi import APIRouter, Depends, status
from src.api.dependencies import (
    get_current_user,
    get_owned_task,
    get_task_service,
)
from src.connectors.database.models import Task, User
from src.schemas.tasks import (
    CreateTaskRequest,
    ListTaskResponse,
    TaskDetailResponse,
    TaskResponse,
    TaskSearchRequest,
    UpdateTaskRequest,
)
from src.services.tasks.service import TaskService

router = APIRouter(prefix='/tasks', tags=['Tasks'])


@router.post(
    '/search',
    response_model=ListTaskResponse,
    summary='Search tasks',
    description=(
        'Search **your** tasks with optional filters. '
        'Set `finished_within_weeks` to **0** to disable '
        'the time window filter.'
    ),
    responses=AUTH_RESPONSES,
)
async def search_tasks(
    body: TaskSearchRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> ListTaskResponse:
    """
    Search tasks for the authenticated user.

    When ``finished_within_weeks`` is 0, the filter is ignored and all matching
    tasks are returned regardless of finish date.

    :param body: Search filters.
    :param current_user: Authenticated user dependency.
    :param task_service: Task service dependency.
    :returns: Filtered task list with metadata.
    """
    finished_within_weeks = (
        None if body.finished_within_weeks == 0 else body.finished_within_weeks
    )
    tasks = await task_service.list(
        user_id=current_user.id,
        statuses=body.statuses,
        priorities=body.priorities,
        task_types=body.task_types,
        finished_within_weeks=finished_within_weeks,
    )
    return ListTaskResponse(
        count=len(tasks),
        finished_within_weeks=body.finished_within_weeks,
        tasks=[TaskResponse.model_validate(task) for task in tasks],
    )


@router.post(
    '',
    response_model=TaskDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create task',
    description='Create a new task owned by the authenticated user.',
    responses={400: RESPONSE_400, **AUTH_RESPONSES},
)
async def create_task(
    body: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> TaskDetailResponse:
    """
    Create a task for the authenticated user.

    :param body: Task creation payload.
    :param current_user: Authenticated user dependency.
    :param task_service: Task service dependency.
    :returns: Created task.
    """
    task = await task_service.create(
        user_id=current_user.id,
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        task_type=body.task_type,
        pull_request_url=body.pull_request_url,
    )
    return TaskDetailResponse.model_validate(task)


@router.get(
    '/{task_id}',
    response_model=TaskDetailResponse,
    summary='Get task by ID',
    description='Return a single task. Only the owner can access it.',
    responses=TASK_OWNER_RESPONSES,
)
async def get_task(
    task: Task = Depends(get_owned_task),
) -> TaskDetailResponse:
    """
    Return a task by identifier.

    Only the task owner may access it.

    :param task: Task owned by the authenticated user.
    :returns: Task data.
    """
    return TaskDetailResponse.model_validate(task)


@router.put(
    '/{task_id}',
    response_model=TaskDetailResponse,
    summary='Update task',
    description='Partial update of a task. Only the owner can modify it.',
    responses={400: RESPONSE_400, **TASK_OWNER_RESPONSES},
)
async def update_task(
    task_id: UUID,
    body: UpdateTaskRequest,
    _task: Task = Depends(get_owned_task),
    task_service: TaskService = Depends(get_task_service),
) -> TaskDetailResponse:
    """
    Update a task by identifier.

    Only the task owner may update it.

    :param task_id: Task identifier.
    :param body: Fields to update.
    :param _task: Ensures the caller owns the task.
    :param task_service: Task service dependency.
    :returns: Updated task data.
    """
    updated = await task_service.update(
        task_id,
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        task_type=body.task_type,
        pull_request_url=body.pull_request_url,
    )
    return TaskDetailResponse.model_validate(updated)


@router.delete(
    '/{task_id}',
    response_model=TaskDetailResponse,
    summary='Delete task',
    description=(
        'Delete a task and return its final state. '
        'Only the owner can delete it.'
    ),
    responses=TASK_OWNER_RESPONSES,
)
async def delete_task(
    task_id: UUID,
    _task: Task = Depends(get_owned_task),
    task_service: TaskService = Depends(get_task_service),
) -> TaskDetailResponse:
    """
    Delete a task by identifier.

    Only the task owner may delete it.

    :param task_id: Task identifier.
    :param _task: Ensures the caller owns the task.
    :param task_service: Task service dependency.
    :returns: Deleted task data.
    """
    deleted = await task_service.delete(task_id)
    return TaskDetailResponse.model_validate(deleted)
