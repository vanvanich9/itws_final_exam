"""Unit tests for task API schemas."""

import uuid
from datetime import datetime
from types import SimpleNamespace

from core.config.enums import PriorityTask, StatusTask, TypeTask
from src.schemas.tasks import TaskDetailResponse, TaskResponse


def test_task_response_from_attributes():
    """Verify TaskResponse maps from an ORM-like object."""
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    source = SimpleNamespace(
        id=task_id,
        user_id=user_id,
        title='Task title',
        status=StatusTask.IN_PROGRESS,
        priority=PriorityTask.HIGH,
        description='hidden in summary',
    )

    response = TaskResponse.model_validate(source)

    assert response.id == task_id
    assert response.user_id == user_id
    assert response.title == 'Task title'
    assert response.status is StatusTask.IN_PROGRESS
    assert response.priority is PriorityTask.HIGH


def test_task_detail_response_maps_type_field():
    """Verify TaskDetailResponse reads the ORM type attribute."""
    now = datetime(2024, 1, 1, 10, 0, 0)
    source = SimpleNamespace(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title='Task title',
        description=None,
        status=StatusTask.BACKLOG,
        priority=PriorityTask.LOW,
        type=TypeTask.BUG,
        pull_request_url=None,
        created_at=now,
        updated_at=now,
    )

    response = TaskDetailResponse.model_validate(source)

    assert response.task_type is TypeTask.BUG


def test_task_detail_response_serializes_task_type_key():
    """Verify TaskDetailResponse serializes the field as ``task_type``."""
    now = datetime(2024, 1, 1, 10, 0, 0)
    source = SimpleNamespace(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title='Task title',
        description=None,
        status=StatusTask.BACKLOG,
        priority=PriorityTask.LOW,
        type=TypeTask.FEATURE,
        pull_request_url=None,
        created_at=now,
        updated_at=now,
    )

    dumped = TaskDetailResponse.model_validate(source).model_dump(
        by_alias=True,
    )

    assert dumped['task_type'] == TypeTask.FEATURE
    assert 'type' not in dumped
