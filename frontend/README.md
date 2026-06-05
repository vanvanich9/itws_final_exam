# TaskBoard — Frontend

Single-page application for managing personal tasks on a Kanban board. Built with SvelteKit 5 and Svelte 5 runes, it communicates with the backend REST API through a server-side proxy.

## Tech Stack

| Layer      | Technology                                                  |
| ---------- | ----------------------------------------------------------- |
| Framework  | SvelteKit 2                                                 |
| UI library | Svelte 5 (runes: `$state`, `$derived`, `$effect`, `$props`) |
| Language   | TypeScript                                                  |
| Build tool | Vite 5                                                      |
| Adapter    | `@sveltejs/adapter-node`                                    |
| Unit tests | Vitest + Testing Library                                    |
| E2E tests  | Playwright                                                  |
| Linting    | ESLint 9 + `eslint-plugin-svelte`                           |
| Formatting | Prettier + `prettier-plugin-svelte`                         |

## Features

- **Authentication** — login and registration pages with client-side validation
- **Session management** — access token in memory, silent refresh via HTTP-only cookie
- **Kanban board** — six columns matching backend task statuses
- **Drag-and-drop** — move tasks between columns (updates status via API)
- **Task modal** — create, view, edit, and delete tasks
- **Filters** — search by status, priority, type, and completion time window
- **Profile management** — edit name, email, password; delete account
- **Toast notifications** — feedback for successful and failed operations
- **Responsive layout** — horizontal scrolling board with sticky navbar

## Architecture

### API Proxy

All `/api/*` requests are intercepted by a SvelteKit server hook (`src/hooks.server.ts`) and forwarded to the backend. The browser always calls same-origin URLs (e.g. `POST /api/users/login`), which:

- Eliminates CORS preflight requests
- Allows `credentials: 'include'` for refresh-token cookies without cross-origin issues

```
Browser  →  SvelteKit server  →  FastAPI backend
           (hooks.server.ts)     (BACKEND_URL)
```

Set `PUBLIC_API_URL` to an empty string so the client uses relative paths. Set `BACKEND_URL` to the actual backend address (used only server-side).

### Client-Side Rendering

The app disables SSR (`ssr = false` in the root layout). All pages are rendered in the browser. On startup, the root layout attempts to restore the session by calling `GET /api/users/me`, with automatic token refresh on 401.

### State Management

Svelte 5 rune-based stores (plain classes exported as singletons):

| Store        | File                              | Responsibility             |
| ------------ | --------------------------------- | -------------------------- |
| `authStore`  | `src/lib/stores/auth.svelte.ts`   | Current user, login/logout |
| `tasksStore` | `src/lib/stores/tasks.svelte.ts`  | Task list, CRUD, filtering |
| `toastStore` | `src/lib/stores/toasts.svelte.ts` | Notification queue         |

### API Client

`src/lib/api/client.ts` provides a typed `fetch` wrapper with:

- Automatic `Authorization: Bearer` header injection
- Silent token refresh on 401 (except for auth endpoints)
- Structured error parsing via `FetchError` / `parseApiError`

Domain-specific API modules:

- `src/lib/api/users.ts` — register, login, logout, profile
- `src/lib/api/tasks.ts` — search, create, update, delete

## Routes

| Path        | File                           | Description                       |
| ----------- | ------------------------------ | --------------------------------- |
| `/`         | `routes/+page.svelte`          | Redirects to `/board` or `/login` |
| `/login`    | `routes/login/+page.svelte`    | Login form                        |
| `/register` | `routes/register/+page.svelte` | Registration form                 |
| `/board`    | `routes/board/+page.svelte`    | Kanban board (auth required)      |

The board layout (`routes/board/+layout.ts`) guards the route — unauthenticated users are redirected to `/login`.

## Project Structure

```
frontend/
├── src/
│   ├── hooks.server.ts          # API proxy to backend
│   ├── app.html / app.css       # Global HTML shell and styles
│   ├── routes/                  # SvelteKit pages and layouts
│   └── lib/
│       ├── api/                 # HTTP client and API modules
│       ├── components/
│       │   ├── board/           # BoardColumn, TaskCard
│       │   ├── layout/          # Navbar, UserMenu, ProfileModal
│       │   ├── tasks/           # FilterBar, TaskModal
│       │   └── ui/              # Button, Input, Modal, Badge, etc.
│       ├── stores/              # Reactive state (auth, tasks, toasts)
│       ├── types/               # TypeScript interfaces
│       ├── utils/               # Error parsing, date formatting
│       └── validation/          # Client-side form validation
├── tests/
│   ├── unit/                    # Vitest unit tests
│   ├── e2e/                     # Playwright end-to-end tests
│   └── setup.ts                 # Test environment setup
├── Dockerfile
├── docker-compose.test.yml
├── playwright.config.ts
├── svelte.config.js
├── vite.config.ts
└── package.json
```

## Getting Started

### Docker (recommended)

From the repository root:

```bash
docker compose up --build
```

The frontend is available at [http://localhost:3000](http://localhost:3000). It waits for the backend health check before starting.

### Local development

**Requirements:** Node.js 20+, running backend instance.

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

By default, Vite dev server runs on port `5173`. Set `BACKEND_URL=http://localhost:8000` in `.env` so the API proxy can reach the backend.

For local dev with the same port as Docker, use:

```bash
npm run dev -- --port 3000
```

## Environment Variables

| Variable         | Scope           | Default                 | Description                                                     |
| ---------------- | --------------- | ----------------------- | --------------------------------------------------------------- |
| `PUBLIC_API_URL` | Client + server | `""`                    | Base URL for API calls. Empty string = same-origin (proxy mode) |
| `BACKEND_URL`    | Server only     | `http://localhost:8000` | Backend address for the API proxy hook                          |
| `ORIGIN`         | Server          | —                       | Public origin URL (used by Playwright and preview server)       |

See [.env.example](./.env.example) for a template.

In Docker Compose, `PUBLIC_API_URL` is empty and `BACKEND_URL` points to `http://backend:8000` inside the network.

## Development Commands

```bash
npm run dev            # Start Vite dev server
npm run build          # Production build
npm run preview        # Preview production build

make fmt               # Prettier format
make lint              # Prettier + ESLint auto-fix
make test              # Full CI test suite via Docker
```

### Individual test commands

```bash
npm run lint:check     # Prettier check + ESLint (no auto-fix)
npm run check          # Svelte type checking (svelte-check)
npm run test:unit      # Vitest unit tests
npm run test:e2e       # Playwright E2E tests (starts preview server)
npm run test:ci        # All checks: lint + types + unit + e2e
```

## Testing

### Unit Tests (Vitest)

Located in `tests/unit/`. Cover validation logic, error parsing, and formatting utilities.

```bash
npm run test:unit
npm run test:unit:watch   # watch mode
```

### End-to-End Tests (Playwright)

Located in `tests/e2e/`. Test full user flows against a built preview server:

- **auth.spec.ts** — registration, login, logout, session persistence
- **board.spec.ts** — column display, task CRUD, drag-and-drop, filtering

Playwright config (`playwright.config.ts`) starts `npm run build && npm run preview` on port `4173` automatically.

The `make test` target uses `docker-compose.test.yml`, which spins up PostgreSQL, the backend, and runs the full `npm run test:ci` pipeline inside a Playwright Docker image.

## UI Components

Reusable components in `src/lib/components/ui/`:

| Component     | Purpose                                                |
| ------------- | ------------------------------------------------------ |
| `Button`      | Primary, secondary, danger variants with loading state |
| `Input`       | Text input with label and error display                |
| `Select`      | Dropdown select                                        |
| `Modal`       | Accessible dialog overlay                              |
| `Badge`       | Status/priority/type labels with color coding          |
| `Spinner`     | Loading indicator                                      |
| `ErrorBanner` | Error message with optional retry action               |
| `Toast`       | Auto-dismissing notification                           |

Board-specific components handle drag-and-drop events natively (HTML5 Drag and Drop API) without external libraries.

## Production Build

```bash
npm run build
node build
```

The [Dockerfile](./Dockerfile) `prod` target builds the app and runs it with Node.js. The [entrypoint.sh](./entrypoint.sh) script builds on startup in `dev` mode and executes `node build` in all environments.

## Type Safety

TypeScript interfaces in `src/lib/types/` mirror the backend Pydantic schemas:

- `task.ts` — `TaskStatus`, `TaskPriority`, `TaskType`, request/response shapes
- `user.ts` — `User`, `LoginRequest`, `RegisterRequest`, etc.

Client-side validation in `src/lib/validation/` enforces the same password and email rules as the backend before submitting forms.
