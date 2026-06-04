"""Alembic migration integration tests."""


async def test_migrations_applied(
    migrated_schema,
    initial_migration_revision,
):
    """
    Verify initial migration created expected tables.

    :param migrated_schema: Applied migration version and tables.
    :param initial_migration_revision: Expected Alembic revision.
    """
    version, tables = migrated_schema

    assert version == initial_migration_revision
    assert 'users' in tables
    assert 'tasks' in tables
