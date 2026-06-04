"""User database connector integration tests."""


async def test_user_create_and_get_by_id(user_connector, user):
    """
    Verify user can be fetched by identifier after creation.

    :param user_connector: User database connector.
    :param user: Created user fixture.
    """
    found = await user_connector.get_by_id(user.id)

    assert found is not None
    assert found.id == user.id
    assert found.email == user.email
    assert found.name == user.name


async def test_user_get_by_email(user_connector, user):
    """
    Verify a user can be fetched by email and missing emails return None.

    :param user_connector: User database connector.
    :param user: Created user fixture.
    """
    found = await user_connector.get_by_email(user.email)
    missing = await user_connector.get_by_email('missing@example.com')

    assert found is not None
    assert found.id == user.id
    assert missing is None


async def test_user_update(user_connector, user):
    """
    Verify user fields can be updated.

    :param user_connector: User database connector.
    :param user: Created user fixture.
    """
    updated = await user_connector.update(
        user,
        name='Updated User',
        email=f'updated-{user.id.hex[:8]}@example.com',
    )

    assert updated is not None
    assert updated.name == 'Updated User'
    assert updated.email.endswith('@example.com')


async def test_user_delete(user_connector, user):
    """
    Verify user can be deleted.

    :param user_connector: User database connector.
    :param user: Created user fixture.
    """
    deleted = await user_connector.delete(user)
    found = await user_connector.get_by_id(user.id)

    assert deleted is not None
    assert deleted.id == user.id
    assert found is None
