async def test_ping(api_client):
    response = await api_client.get('/api/ping/')

    assert response.status_code == 200
    assert response.json() == {'message': 'pong'}
