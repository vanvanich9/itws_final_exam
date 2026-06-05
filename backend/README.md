# TaskBoard — Backend

REST API for user accounts and personal task management. Built with FastAPI and PostgreSQL, it provides JWT-based authentication and a full CRUD interface for tasks scoped to the authenticated user.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Runtime | Python 3.11 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2 (async) |
| Database driver | asyncpg |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | PyJWT + bcrypt |
| Server | Gunicorn + Uvicorn workers |
| Linting / formatting | Ruff |
| Testing | pytest, pytest-asyncio, httpx |

## Architecture

The backend follows a layered design that separates HTTP concerns from business logic and persistence:

```
src/
├── api/              # HTTP routes, dependencies, exception handlers
├── schemas/          # Pydantic request/response models
├── services/         # Business logic (users, tasks)
├── connectors/
│   └── database/     # SQLAlchemy models, Alembic, DB connectors
├── logic/            # Auth helpers, domain models, shared errors
└── app.py            # Application factory and lifespan
core/
├── config/           # Enums, OpenAPI metadata, auth constants
└── settings/         # Pydantic Settings (env-based configuration)
```

**Request flow:**

1. FastAPI route receives the request and validates the body via Pydantic schemas.
2. Dependencies resolve the current user (`get_current_user`) and inject services from `app.state`.
3. Service layer (`UserService`, `TaskService`) applies business rules.
4. Database connectors execute async SQLAlchemy queries against PostgreSQL.

Services and connectors are initialized once in the application lifespan (`create_app` → `lifespan`) and stored on `app.state`.

## API Endpoints

All routes are prefixed with `/api`. Interactive documentation is available at `/docs` (Swagger UI) and `/redoc`.

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/ping` | No | Health check |

### Users

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/users/register` | No | Create a new account |
| `POST` | `/api/users/login` | No | Authenticate; returns access token, sets refresh cookie |
| `POST` | `/api/users/refresh` | Cookie | Exchange refresh token for a new access token |
| `POST` | `/api/users/logout` | No | Clear the refresh token cookie |
| `GET` | `/api/users/me` | Bearer | Get the current user's profile |
| `GET` | `/api/users/{user_id}` | Bearer | Get any user's profile by ID |
| `PUT` | `/api/users/{user_id}` | Bearer (owner) | Update own profile |
| `DELETE` | `/api/users/{user_id}` | Bearer (owner) | Delete own account |

### Tasks

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/tasks/search` | Bearer | Search tasks with optional filters |
| `POST` | `/api/tasks` | Bearer | Create a new task |
| `GET` | `/api/tasks/{task_id}` | Bearer (owner) | Get task details |
| `PUT` | `/api/tasks/{task_id}` | Bearer (owner) | Update a task |
| `DELETE` | `/api/tasks/{task_id}` | Bearer (owner) | Delete a task |

## Authentication

The API uses a dual-token JWT scheme:

- **Access token** — returned in the JSON body on login/refresh. Sent by clients as `Authorization: Bearer <token>`. Short-lived.
- **Refresh token** — stored in an HTTP-only cookie (`refresh_token`). Used by `POST /api/users/refresh` to obtain a new access token without re-entering credentials. Rotated on each refresh.

Password requirements (enforced at registration and update):

- 8–20 characters
- At least one lowercase letter, one uppercase letter, and one special character

## Domain Model

### User

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `email` | string | Unique |
| `password` | string | bcrypt hash |
| `name` | string | Display name |
| `created_at` / `updated_at` | datetime | Auto-managed |

### Task

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK → users |
| `title` | string | Required, max 255 chars |
| `description` | text | Optional |
| `status` | enum | `backlog`, `to_do`, `in_progress`, `on_review`, `done`, `cancelled` |
| `priority` | enum | `low`, `medium`, `high`, `critical` |
| `type` | enum | `feature`, `bug`, `documentation`, `other` |
| `pull_request_url` | string | Optional |
| `created_at` / `updated_at` | datetime | Auto-managed |

### Task Search Filters

`POST /api/tasks/search` accepts:

| Filter | Type | Description |
|--------|------|-------------|
| `statuses` | list of status enums | Match any of the given statuses |
| `priorities` | list of priority enums | Match any of the given priorities |
| `task_types` | list of type enums | Match any of the given types |
| `finished_within_weeks` | integer | Only include `done` tasks finished within N weeks. Set to `0` to disable this filter |

## Getting Started

### Docker (recommended)

From the repository root:

```bash
docker compose up --build backend
```

The `init_db` service runs Alembic migrations automatically before the backend starts.

### Local development (Poetry)

**Requirements:** Python 3.11+, Poetry, running PostgreSQL instance.

```bash
cd backend
cp .env.example .env        # adjust DATABASE_* values if needed
poetry install
poetry run alembic -c src/connectors/database/alembic.ini upgrade head
poetry run gunicorn src.asgi:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --reload
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | JWT signing key (must be long enough for HS256) |
| `DEBUG` | `false` | When `true`, refresh cookies are not marked `Secure` |
| `CORS_ORIGINS` | `[]` | JSON array of allowed origins |
| `DATABASE_HOST` | `localhost` | PostgreSQL host |
| `DATABASE_PORT` | `5432` | PostgreSQL port |
| `DATABASE_USERNAME` | `postgres` | Database user |
| `DATABASE_PASSWORD` | `postgres` | Database password |
| `DATABASE_NAME` | `db` | Database name |

See [.env.example](./.env.example) for a ready-to-copy template.

## Database Migrations

Alembic configuration lives at `src/connectors/database/alembic.ini`. Migrations are in `src/connectors/database/alembic/versions/`.

```bash
# Apply all pending migrations
poetry run alembic -c src/connectors/database/alembic.ini upgrade head

# Create a new migration (after model changes)
poetry run alembic -c src/connectors/database/alembic.ini revision --autogenerate -m "description"
```

## Development Commands

```bash
make fmt    # Ruff format
make lint   # Ruff format + lint with auto-fix
make test   # Full test suite via Docker Compose
```

### Running tests locally

```bash
poetry run ruff check core src tests
poetry run pytest tests/unit
poetry run pytest tests/integration   # requires a running backend + database
```

The `make test` target spins up an isolated stack (`docker-compose.test.yml`) with a tmpfs-backed PostgreSQL instance, applies migrations, starts the API, and runs both unit and integration test suites.

## Test Structure

```
tests/
├── unit/
│   ├── api/          # Route handlers, dependencies, OpenAPI
│   ├── config/       # Settings and enums
│   ├── logic/        # Auth, errors, cookie helpers
│   ├── schemas/      # Pydantic model validation
│   └── services/     # UserService unit tests
└── integration/
    ├── api/          # End-to-end HTTP tests against a live server
    └── db/           # Database connector and migration tests
```

## Docker Images

The [Dockerfile](./Dockerfile) defines three targets:

| Target | Purpose |
|--------|---------|
| `dev` | Development server with hot-reload volumes |
| `test` | Test runner with dev dependencies installed |
| `prod` | Production image with application code baked in |

The entrypoint runs Gunicorn with Uvicorn workers:

```bash
gunicorn src.asgi:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Error Handling

API exceptions are registered centrally in `src/api/exceptions.py`. Domain-level errors from the service layer (e.g. `UserNotFoundError`, `TaskNotFoundError`, `DuplicateEmailError`) are mapped to appropriate HTTP status codes with consistent JSON error bodies.
