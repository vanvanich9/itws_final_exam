"""OpenAPI metadata for the FastAPI application."""

from typing import Any

EXAMPLE_UUID = '3fa85f64-5717-4562-b3fc-2c963f66afa6'

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        'name': 'Users',
        'description': (
            'Registration, login, token refresh, and profile management. '
            'Protected routes require a Bearer access token.'
        ),
    },
    {
        'name': 'Tasks',
        'description': (
            'Create, search, update, and delete tasks. '
            'All routes require authentication; '
            'you can only access your own tasks.'
        ),
    },
    {
        'name': 'Health',
        'description': 'Service health check.',
    },
]

RESPONSE_400: dict[str, Any] = {
    'description': 'Invalid request (validation or business rules).',
}
RESPONSE_401: dict[str, Any] = {
    'description': 'Missing or invalid access token.',
}
RESPONSE_403: dict[str, Any] = {
    'description': 'Authenticated but not allowed to access this resource.',
}
RESPONSE_404: dict[str, Any] = {
    'description': 'Resource not found.',
}
RESPONSE_409: dict[str, Any] = {
    'description': 'Conflict with existing data.',
}

AUTH_RESPONSES: dict[int, dict[str, Any]] = {
    401: RESPONSE_401,
}

TASK_OWNER_RESPONSES: dict[int, dict[str, Any]] = {
    401: RESPONSE_401,
    403: RESPONSE_403,
    404: RESPONSE_404,
}
