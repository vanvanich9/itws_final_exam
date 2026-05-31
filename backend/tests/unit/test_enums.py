"""Enum helper unit tests."""

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
    """
    Verify enum_values returns member values for task enums.

    :param enum_cls: Enum class under test.
    :param expected: Expected enum values.
    """
    assert enum_values(enum_cls) == expected


def test_enum_values_uses_member_values_not_names():
    """Verify enum_values returns values rather than member names."""
    values = enum_values(StatusTask)

    assert StatusTask.BACKLOG.value in values
    assert StatusTask.BACKLOG.name not in values
