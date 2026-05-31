import pytest
from core.config.enums import PriorityTask, StatusTask, TypeTask
from src.logic.enums import enum_values


@pytest.mark.parametrize(
    ('enum_cls', 'expected'),
    [
        (
            StatusTask,
            [
                'backlog',
                'to_do',
                'in_progress',
                'on_review',
                'done',
                'cancelled',
            ],
        ),
        (PriorityTask, ['low', 'medium', 'high', 'critical']),
        (TypeTask, ['feature', 'bug', 'documentation', 'other']),
    ],
)
def test_enum_values(enum_cls, expected):
    assert enum_values(enum_cls) == expected


def test_enum_values_uses_member_values_not_names():
    values = enum_values(StatusTask)

    assert StatusTask.BACKLOG.value in values
    assert StatusTask.BACKLOG.name not in values
