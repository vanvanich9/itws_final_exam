from enum import StrEnum


class StatusTask(StrEnum):
    BACKLOG = 'backlog'
    TO_DO = 'to_do'
    IN_PROGRESS = 'in_progress'
    ON_REVIEW = 'on_review'
    DONE = 'done'
    CANCELLED = 'cancelled'


class PriorityTask(StrEnum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class TypeTask(StrEnum):
    FEATURE = 'feature'
    BUG = 'bug'
    DOCUMENTATION = 'documentation'
    OTHER = 'other'
