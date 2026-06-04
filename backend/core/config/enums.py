"""Task-related enum definitions."""

from enum import StrEnum


class StatusTask(StrEnum):
    """Task workflow status."""

    BACKLOG = 'backlog'
    TO_DO = 'to_do'
    IN_PROGRESS = 'in_progress'
    ON_REVIEW = 'on_review'
    DONE = 'done'
    CANCELLED = 'cancelled'


class PriorityTask(StrEnum):
    """Task priority level."""

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class TypeTask(StrEnum):
    """Task type."""

    FEATURE = 'feature'
    BUG = 'bug'
    DOCUMENTATION = 'documentation'
    OTHER = 'other'


class TokenType(StrEnum):
    """JWT token purpose."""

    ACCESS = 'access_token'
    REFRESH = 'refresh_token'
