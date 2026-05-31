"""Enum helpers for domain and persistence layers."""

from enum import Enum


def enum_values(enum_cls: type[Enum]) -> list[str]:
    """
    Return enum member values for SQLAlchemy PostgreSQL enums.

    :param enum_cls: Python enum class.
    :returns: List of enum values.
    """
    return [member.value for member in enum_cls]
