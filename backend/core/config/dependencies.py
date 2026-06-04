"""FastAPI dependency configuration."""

from fastapi.security import HTTPBearer

BEARER_SCHEME = HTTPBearer(auto_error=False)
