"""Task database connector integration tests."""

from datetime import UTC, datetime, timedelta

from core.config.enums import PriorityTask, StatusTask, TypeTask


async def test_task_create_without_description(task_connector, user):
    """
    Verify task can be created without description.

    :param task_connector: Task database connector.
    :param user: Owner user fixture.
    """
    created = await task_connector.create(
        user_id=user.id,
        title='Title only',
    )
    found = await task_connector.get_by_id(created.id)

    assert found is not None
    assert found.title == 'Title only'
    assert found.description is None


async def test_task_create_and_get_by_id(task_connector, task, user):
    """
    Verify task can be fetched by identifier after creation.

    :param task_connector: Task database connector.
    :param task: Created task fixture.
    :param user: Owner user fixture.
    """
    found = await task_connector.get_by_id(task.id)

    assert found is not None
    assert found.id == task.id
    assert found.user_id == user.id
    assert found.title == task.title


async def test_task_list_filters(task_connector, task, user):
    """
    Verify task list filters by user, status, priority, and type.

    :param task_connector: Task database connector.
    :param task: Existing task fixture.
    :param user: Owner user fixture.
    """
    await task_connector.create(
        user_id=user.id,
        title='Filtered task',
        description='Description',
        status=StatusTask.IN_PROGRESS,
        priority=PriorityTask.HIGH,
        task_type=TypeTask.FEATURE,
    )

    by_user = await task_connector.list(user_id=user.id)
    by_status = await task_connector.list(
        user_id=user.id,
        statuses=[StatusTask.IN_PROGRESS],
    )
    by_priority = await task_connector.list(
        user_id=user.id,
        priorities=[PriorityTask.HIGH],
    )
    by_type = await task_connector.list(
        user_id=user.id,
        task_types=[TypeTask.FEATURE],
    )
    empty_status = await task_connector.list(statuses=[])

    assert len(by_user) >= 2
    assert len(by_status) >= 1
    assert all(t.status == StatusTask.IN_PROGRESS for t in by_status)
    assert len(by_priority) >= 1
    assert len(by_type) >= 1
    assert empty_status == []


async def test_task_finished_within_weeks(task_connector, user):
    """
    Verify finished_within_weeks excludes stale done tasks.

    :param task_connector: Task database connector.
    :param user: Owner user fixture.
    """
    old_done = await task_connector.create(
        user_id=user.id,
        title='Old done',
        description='Description',
        status=StatusTask.DONE,
    )
    async with task_connector.session() as sess:
        row = await sess.merge(old_done)
        row.updated_at = datetime.now(UTC) - timedelta(weeks=3)
        row.updated_at = row.updated_at.replace(tzinfo=None)
        await sess.flush()

    recent_done = await task_connector.create(
        user_id=user.id,
        title='Recent done',
        description='Description',
        status=StatusTask.DONE,
    )
    active = await task_connector.create(
        user_id=user.id,
        title='Active',
        description='Description',
        status=StatusTask.IN_PROGRESS,
    )

    actual = await task_connector.list(
        user_id=user.id,
        finished_within_weeks=2,
    )
    actual_ids = {item.id for item in actual}

    assert recent_done.id in actual_ids
    assert active.id in actual_ids
    assert old_done.id not in actual_ids


async def test_task_update(task_connector, task):
    """
    Verify task fields can be updated.

    :param task_connector: Task database connector.
    :param task: Created task fixture.
    """
    updated = await task_connector.update(
        task,
        title='Updated title',
        status=StatusTask.DONE,
        priority=PriorityTask.CRITICAL,
        task_type=TypeTask.BUG,
        pull_request_url='https://example.com/pr/1',
    )

    assert updated is not None
    assert updated.title == 'Updated title'
    assert updated.status == StatusTask.DONE
    assert updated.priority == PriorityTask.CRITICAL
    assert updated.type == TypeTask.BUG
    assert updated.pull_request_url == 'https://example.com/pr/1'


async def test_task_delete(task_connector, task):
    """
    Verify task can be deleted.

    :param task_connector: Task database connector.
    :param task: Created task fixture.
    """
    deleted = await task_connector.delete(task)
    found = await task_connector.get_by_id(task.id)

    assert deleted is not None
    assert deleted.id == task.id
    assert found is None
