"""Smoke tests for OpenAPI schema generation."""

from src.app import create_app


def test_openapi_schema_generates():
    """Verify the OpenAPI schema builds without errors for all routes."""
    schema = create_app().openapi()

    assert schema['info']['title'] == 'Task Manager API'
    paths = schema['paths']
    assert '/api/tasks/search' in paths
    assert '/api/tasks' in paths
    assert '/api/tasks/{task_id}' in paths
    assert '/api/users/register' in paths
