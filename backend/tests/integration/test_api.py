"""API integration tests."""


async def test_ping(api_client):
    """
    Verify ping endpoint returns pong.

    :param api_client: HTTP client fixture.
    """
    response = await api_client.get('/api/ping/')

    assert response.status_code == 200
    assert response.json() == {'message': 'pong'}
