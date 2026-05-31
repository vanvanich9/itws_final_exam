from enum import Enum


class StatusTask(str, Enum):
    BACKLOG = 'backlog'
    TO_DO = 'to_do'
    IN_PROGRESS = 'in_progress'
    ON_REVIEW = 'on_review'
    DONE = 'done'
    CANCELLED = 'cancelled'


class PriorityTask(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class TypeTask(str, Enum):
    FEATURE = 'feature'
    BUG = 'bug'
    DOCUMENTATION = 'documentation'
    OTHER = 'other'
