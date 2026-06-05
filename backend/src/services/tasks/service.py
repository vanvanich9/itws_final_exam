"""Task service for Task Manager task operations."""

from uuid import UUID

from core.config.enums import PriorityTask, StatusTask, TypeTask
from src.connectors.database.models import Task
from src.connectors.database.services.tasks import TaskDatabaseConnector
from src.services.tasks.errors import InvalidTitleError, TaskNotFoundError


class TaskService:
    """Task service."""

    def __init__(self, task_database: TaskDatabaseConnector) -> None:
        """
        Initialize the task service.

        :param task_database: Task database connector.
        """
        self.task_database = task_database

    async def get_by_id(self, task_id: UUID) -> Task:
        """
        Fetch a task by identifier.

        :param task_id: Task identifier.
        :returns: Task instance.
        :raises TaskNotFoundError: When the task does not exist.
        """
        task = await self.task_database.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError
        return task

    async def list(
        self,
        user_id: UUID | None = None,
        statuses: list[StatusTask] | None = None,
        priorities: list[PriorityTask] | None = None,
        task_types: list[TypeTask] | None = None,
        finished_within_weeks: int | None = None,
    ) -> list[Task]:
        """
        List tasks with optional filters.

        :param user_id: Filter by owner, if provided.
        :param statuses: Filter by statuses, if provided.
        :param priorities: Filter by priorities, if provided.
        :param task_types: Filter by task types, if provided.
        :param finished_within_weeks: When set, include done/cancelled tasks
            only if finished within this many weeks; always include other
            statuses.
        :returns: Matching tasks.
        """
        return await self.task_database.list(
            user_id=user_id,
            statuses=statuses,
            priorities=priorities,
            task_types=task_types,
            finished_within_weeks=finished_within_weeks,
        )

    async def create(
        self,
        user_id: UUID,
        title: str,
        description: str | None = None,
        status: StatusTask = StatusTask.BACKLOG,
        priority: PriorityTask = PriorityTask.LOW,
        task_type: TypeTask = TypeTask.OTHER,
        pull_request_url: str | None = None,
    ) -> Task:
        """
        Create a new task.

        :param user_id: Owner user identifier.
        :param title: Task title.
        :param description: Task description, if provided.
        :param status: Task status.
        :param priority: Task priority.
        :param task_type: Task type.
        :param pull_request_url: Optional pull request URL.
        :returns: Created task.
        :raises InvalidTitleError: When the title is empty or whitespace only.
        """
        if not title.strip():
            raise InvalidTitleError
        return await self.task_database.create(
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            task_type=task_type,
            pull_request_url=pull_request_url,
        )

    async def update(
        self,
        task_id: UUID,
        user_id: UUID | None = None,
        title: str | None = None,
        description: str | None = None,
        status: StatusTask | None = None,
        priority: PriorityTask | None = None,
        task_type: TypeTask | None = None,
        pull_request_url: str | None = None,
    ) -> Task:
        """
        Update a task.

        :param task_id: Task identifier.
        :param user_id: New owner identifier, if provided.
        :param title: New title, if provided.
        :param description: New description, if provided.
        :param status: New status, if provided.
        :param priority: New priority, if provided.
        :param task_type: New task type, if provided.
        :param pull_request_url: New pull request URL, if provided.
        :returns: Updated task.
        :raises TaskNotFoundError: When the task does not exist.
        :raises InvalidTitleError: When the title is empty or whitespace only.
        """
        if title is not None and not title.strip():
            raise InvalidTitleError
        task = await self.get_by_id(task_id)
        return await self.task_database.update(
            task=task,
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            task_type=task_type,
            pull_request_url=pull_request_url,
        )

    async def delete(self, task_id: UUID) -> Task:
        """
        Delete a task.

        :param task_id: Task identifier.
        :returns: Deleted task.
        :raises TaskNotFoundError: When the task does not exist.
        """
        task = await self.get_by_id(task_id)
        return await self.task_database.delete(task)
