from datetime import datetime
from uuid import UUID, uuid4

from core.config.enums import PriorityTask, StatusTask, TypeTask
from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from src.connectors.database.models._base import Base
from src.logic.enums import enum_values


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey('users.id'), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[StatusTask] = mapped_column(
        Enum(StatusTask, values_callable=enum_values),
        default=StatusTask.BACKLOG,
    )
    priority: Mapped[PriorityTask] = mapped_column(
        Enum(PriorityTask, values_callable=enum_values),
        default=PriorityTask.LOW,
    )
    type: Mapped[TypeTask] = mapped_column(
        Enum(TypeTask, values_callable=enum_values),
        default=TypeTask.OTHER,
    )
    pull_request_url: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
