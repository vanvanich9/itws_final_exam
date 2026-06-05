"""Task API schemas."""

from datetime import datetime
from uuid import UUID

from core.config.enums import PriorityTask, StatusTask, TypeTask
from core.config.openapi import EXAMPLE_UUID
from pydantic import BaseModel, ConfigDict, Field


class TaskSearchRequest(BaseModel):
    """Filters for task search."""

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'statuses': [StatusTask.BACKLOG, StatusTask.IN_PROGRESS],
                'priorities': [PriorityTask.HIGH, PriorityTask.CRITICAL],
                'task_types': [TypeTask.FEATURE, TypeTask.BUG],
                'finished_within_weeks': 0,
            },
        },
    )

    statuses: list[StatusTask] | None = Field(
        default=None,
        description='Include only tasks with these statuses.',
    )
    priorities: list[PriorityTask] | None = Field(
        default=None,
        description='Include only tasks with these priorities.',
    )
    task_types: list[TypeTask] | None = Field(
        default=None,
        description='Include only tasks with these types.',
    )
    finished_within_weeks: int = Field(
        default=0,
        ge=0,
        description=(
            'When **0**, the filter is ignored and all your tasks '
            'are returned. When **> 0**, done/cancelled tasks older '
            'than this many weeks are hidden; other statuses are included.'
        ),
    )


class TaskResponse(BaseModel):
    """Task summary returned by search."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': EXAMPLE_UUID,
                'user_id': EXAMPLE_UUID,
                'title': 'Implement search endpoint',
                'status': StatusTask.IN_PROGRESS,
                'priority': PriorityTask.HIGH,
            },
        },
    )

    id: UUID = Field(description='Task identifier.')
    user_id: UUID = Field(description='Owner user identifier.')
    title: str = Field(description='Task title.')
    status: StatusTask = Field(description='Workflow status.')
    priority: PriorityTask = Field(description='Priority level.')


class ListTaskResponse(BaseModel):
    """Task search result with metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'count': 2,
                'finished_within_weeks': 0,
                'tasks': [
                    {
                        'id': EXAMPLE_UUID,
                        'user_id': EXAMPLE_UUID,
                        'title': 'Implement search endpoint',
                        'status': StatusTask.IN_PROGRESS,
                        'priority': PriorityTask.HIGH,
                    },
                ],
            },
        },
    )

    count: int = Field(description='Number of tasks in `tasks`.')
    finished_within_weeks: int = Field(
        description='Echo of the request filter (0 means filter was ignored).',
    )
    tasks: list[TaskResponse] = Field(description='Matching tasks.')


class CreateTaskRequest(BaseModel):
    """Payload for creating a task."""

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'title': 'Implement search endpoint',
                'description': 'Add POST /api/tasks/search with filters.',
                'status': StatusTask.BACKLOG,
                'priority': PriorityTask.MEDIUM,
                'task_type': TypeTask.FEATURE,
                'pull_request_url': 'https://github.com/org/repo/pull/42',
            },
        },
    )

    title: str = Field(
        min_length=1,
        examples=['Implement search endpoint'],
        description='Task title (required, non-empty).',
    )
    description: str | None = Field(
        default=None,
        examples=['Add POST /api/tasks/search with filters.'],
        description='Optional long description.',
    )
    status: StatusTask = Field(
        default=StatusTask.BACKLOG,
        description='Initial workflow status.',
    )
    priority: PriorityTask = Field(
        default=PriorityTask.LOW,
        description='Initial priority.',
    )
    task_type: TypeTask = Field(
        default=TypeTask.OTHER,
        description='Task category.',
    )
    pull_request_url: str | None = Field(
        default=None,
        examples=['https://github.com/org/repo/pull/42'],
        description='Optional link to a pull request.',
    )


class UpdateTaskRequest(BaseModel):
    """Payload for updating a task (partial update)."""

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'title': 'Implement search endpoint',
                'status': StatusTask.IN_PROGRESS,
                'priority': PriorityTask.HIGH,
            },
        },
    )

    title: str | None = Field(
        default=None,
        description='New title (non-empty when provided).',
    )
    description: str | None = Field(
        default=None,
        description='New description.',
    )
    status: StatusTask | None = Field(
        default=None,
        description='New workflow status.',
    )
    priority: PriorityTask | None = Field(
        default=None,
        description='New priority.',
    )
    task_type: TypeTask | None = Field(
        default=None,
        description='New task category.',
    )
    pull_request_url: str | None = Field(
        default=None,
        description='New pull request URL.',
    )


class TaskDetailResponse(BaseModel):
    """Full task data returned by the API."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': EXAMPLE_UUID,
                'user_id': EXAMPLE_UUID,
                'title': 'Implement search endpoint',
                'description': 'Add POST /api/tasks/search with filters.',
                'status': StatusTask.IN_PROGRESS,
                'priority': PriorityTask.HIGH,
                'task_type': TypeTask.FEATURE,
                'pull_request_url': 'https://github.com/org/repo/pull/42',
                'created_at': '2026-01-01T12:00:00',
                'updated_at': '2026-01-02T12:00:00',
            },
        },
    )

    id: UUID = Field(description='Task identifier.')
    user_id: UUID = Field(description='Owner user identifier.')
    title: str = Field(description='Task title.')
    description: str | None = Field(description='Task description.')
    status: StatusTask = Field(description='Workflow status.')
    priority: PriorityTask = Field(description='Priority level.')
    task_type: TypeTask = Field(
        validation_alias='type',
        serialization_alias='task_type',
        description='Task category.',
    )
    pull_request_url: str | None = Field(
        description='Link to a pull request, if any.',
    )
    created_at: datetime = Field(description='Creation time (UTC).')
    updated_at: datetime = Field(description='Last update time (UTC).')
