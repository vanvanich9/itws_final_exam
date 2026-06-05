# TaskBoard

A full-stack personal task manager with a Kanban-style board. Users can register, log in, and manage their own tasks across workflow columns — from backlog to done.

The project is a monorepo with two independently deployable applications:

| Component | Stack | Port (dev) |
|-----------|-------|------------|
| [Backend](./backend) | Python 3.11, FastAPI, PostgreSQL | `8000` |
| [Frontend](./frontend) | SvelteKit 5, Svelte 5, TypeScript | `3000` |

## Features

- **User accounts** — registration, login, profile management, account deletion
- **JWT authentication** — short-lived access tokens in memory, refresh tokens in HTTP-only cookies
- **Personal task board** — six status columns (Backlog → Done/Cancelled)
- **Task management** — create, view, edit, delete tasks with priority, type, and optional PR link
- **Drag-and-drop** — move tasks between columns on the board
- **Filtering** — search tasks by status, priority, type, and completion time window
- **API documentation** — interactive OpenAPI/Swagger UI at `/docs` on the backend

## Architecture

```
┌─────────────┐     /api/* proxy      ┌─────────────┐     SQL      ┌────────────┐
│   Browser   │ ────────────────────► │  Frontend   │              │            │
│             │ ◄──────────────────── │  (SvelteKit)│              │            │
└─────────────┘                       └──────┬──────┘              │            │
                                             │ server-side         │ PostgreSQL │
                                             │ fetch               │            │
                                             ▼                     │            │
                                       ┌─────────────┐ ───────────►│            │
                                       │   Backend   │             │            │
                                       │  (FastAPI)  │ ◄────────── └────────────┘
                                       └─────────────┘
```

The frontend proxies all `/api/*` requests to the backend through a SvelteKit server hook. From the browser's perspective, every API call is same-origin, which avoids CORS preflight issues and keeps refresh-token cookies working reliably.

## Quick Start (Docker)

**Requirements:** Docker and Docker Compose.

```bash
docker compose up --build
```

This starts four services:

| Service | Description |
|---------|-------------|
| `postgres` | PostgreSQL 17 database |
| `init_db` | Runs Alembic migrations (one-shot) |
| `backend` | FastAPI API server |
| `frontend` | SvelteKit application |

Once all services are healthy:

- **App:** [http://localhost:3000](http://localhost:3000)
- **API:** [http://localhost:8000](http://localhost:8000)
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)

## Development Commands

The root [Makefile](./Makefile) delegates to each subproject:

```bash
make fmt      # Format backend (Ruff) and frontend (Prettier)
make lint     # Lint and auto-fix both projects
make test     # Run full test suites (Docker-based)
```

Individual targets are also available:

```bash
make fmt-backend    make lint-backend    make test-backend
make fmt-frontend   make lint-frontend   make test-frontend
```

See [backend/README.md](./backend/README.md) and [frontend/README.md](./frontend/README.md) for project-specific setup, local development without Docker, and detailed documentation.

## CI

GitHub Actions workflows run on push:

| Workflow | Trigger path | What it runs |
|----------|--------------|--------------|
| [ci-backend.yml](./.github/workflows/ci-backend.yml) | `backend/**` | Ruff lint + unit & integration tests |
| [ci-frontend.yml](./.github/workflows/ci-frontend.yml) | `frontend/**` | ESLint, Prettier, `svelte-check`, Vitest, Playwright |

Both test jobs use Docker Compose test stacks with ephemeral PostgreSQL databases.

## Project Structure

```
.
├── backend/          # FastAPI REST API
├── frontend/         # SvelteKit SPA
├── docker-compose.yml
├── Makefile
└── .github/workflows/
```

## Environment Variables

Each subproject has its own `.env.example`:

- [backend/.env.example](./backend/.env.example) — database credentials, JWT secret, CORS origins
- [frontend/.env.example](./frontend/.env.example) — API URL and backend proxy target

In Docker Compose, these are set inline in `docker-compose.yml`. For local development, copy the examples to `.env` in each directory.

## License

This project was created as part of the ITWS final exam.
