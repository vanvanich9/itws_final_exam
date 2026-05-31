from datetime import UTC, datetime
from uuid import UUID

from core.config.enums import PriorityTask, StatusTask, TypeTask
from core.config.general import MAX_ACTUAL_TIME
from sqlalchemy import or_, select
from src.connectors.database.models import Task
from src.connectors.database.services._base import BaseDatabaseConnector


class TaskDatabaseConnector(BaseDatabaseConnector):
    async def create(
        self,
        user_id: UUID,
        title: str,
        description: str,
        status: StatusTask = StatusTask.BACKLOG,
        priority: PriorityTask = PriorityTask.LOW,
        task_type: TypeTask = TypeTask.OTHER,
        pull_request_url: str | None = None,
    ) -> Task:
        async with self.session() as sess:
            row = Task(
                user_id=user_id,
                title=title,
                description=description,
                status=status,
                priority=priority,
                type=task_type,
                pull_request_url=pull_request_url,
            )
            sess.add(row)
            await sess.flush()
            await sess.refresh(row)
            return row

    async def get_by_id(self, task_id: UUID) -> Task | None:
        async with self.session() as sess:
            return await sess.get(Task, task_id)

    async def list(
        self,
        user_id: UUID | None = None,
        statuses: list[StatusTask] | None = None,
        priorities: list[PriorityTask] | None = None,
        task_types: list[TypeTask] | None = None,
        only_actual_tasks: bool = False,
    ) -> list[Task]:
        if statuses is not None and not statuses:
            return []
        if priorities is not None and not priorities:
            return []
        if task_types is not None and not task_types:
            return []

        async with self.session() as sess:
            stmt = select(Task)
            if user_id is not None:
                stmt = stmt.where(Task.user_id == user_id)
            if statuses is not None:
                stmt = stmt.where(Task.status.in_(statuses))
            if priorities is not None:
                stmt = stmt.where(Task.priority.in_(priorities))
            if task_types is not None:
                stmt = stmt.where(Task.type.in_(task_types))
            if only_actual_tasks:
                cutoff = (datetime.now(UTC) - MAX_ACTUAL_TIME).replace(
                    tzinfo=None
                )
                done_or_cancelled = (
                    StatusTask.DONE,
                    StatusTask.CANCELLED,
                )
                stmt = stmt.where(
                    or_(
                        Task.updated_at >= cutoff,
                        Task.status.not_in(done_or_cancelled),
                    )
                )
            result = await sess.execute(stmt)
            return list(result.scalars().all())

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
    ) -> Task | None:
        async with self.session() as sess:
            row = await sess.get(Task, task_id)
            if row is None:
                return None
            if user_id is not None:
                row.user_id = user_id
            if title is not None:
                row.title = title
            if description is not None:
                row.description = description
            if status is not None:
                row.status = status
            if priority is not None:
                row.priority = priority
            if task_type is not None:
                row.type = task_type
            if pull_request_url is not None:
                row.pull_request_url = pull_request_url
            await sess.flush()
            await sess.refresh(row)
            return row

    async def delete(self, task: Task) -> bool:
        async with self.session() as sess:
            row = await sess.merge(task)
            await sess.delete(row)
            await sess.flush()
            return True
