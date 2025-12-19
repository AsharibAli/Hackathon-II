# Todo Full-Stack Web Application

A modern, secure, multi-user todo application built with **spec-driven development** principles.

## Architecture

**Monorepo Structure:**
- `backend/` - FastAPI (Python) REST API with JWT authentication
- `frontend/` - Next.js 14 (TypeScript) with App Router
- `specs/` - Feature specifications and design documents
- `.specify/` - Spec-Kit Plus configuration and templates

## Tech Stack

### Backend
- **Framework:** FastAPI 0.104+
- **ORM:** SQLModel 0.0.14+
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **Package Manager:** uv

### Frontend
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript 5.x (strict mode)
- **Authentication:** Better Auth with JWT plugin
- **Styling:** Tailwind CSS 4
- **UI Components:** shadcn/ui (Radix UI)
- **Notifications:** Sonner
- **Package Manager:** pnpm

## Features

- ✅ **User Authentication** - Secure registration, login, and logout with JWT tokens
- ✅ **Multi-User Isolation** - Each user can only access their own tasks
- ✅ **Task Management** - Full CRUD operations (Create, Read, Update, Delete)
- ✅ **Task Completion Tracking** - Toggle tasks between complete and incomplete
- ✅ **Task Editing** - Update task titles and descriptions
- ✅ **Task Deletion** - Remove tasks with confirmation dialog
- ✅ **Data Persistence** - PostgreSQL database with SQLModel ORM
- ✅ **Type Safety** - TypeScript (frontend) and SQLModel (backend)
- ✅ **Responsive Design** - Works on desktop and mobile browsers
- ✅ **Error Handling** - Global error boundary and toast notifications
- ✅ **Loading States** - Skeleton loaders for better UX
- ✅ **Optimistic Updates** - Instant UI feedback for user actions

## Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **uv** (Python package manager): `pip install uv`
- **pnpm** (Node package manager): `npm install -g pnpm`
- **Neon PostgreSQL account**: Sign up at https://neon.tech

## Quick Start

See [specs/001-todo-app-baseline/quickstart.md](specs/001-todo-app-baseline/quickstart.md) for detailed setup instructions.

### Backend Setup

```bash
cd backend

# Install dependencies with uv
uv init
uv add fastapi sqlmodel python-jose[cryptography] passlib[bcrypt] python-multipart uvicorn alembic psycopg2-binary

# Configure environment
cp .env.example .env
# Edit .env with your Neon database URL and JWT secret

# Run database migrations
alembic upgrade head

# Start development server
fastapi dev src/main.py
```

Backend will be available at http://localhost:8000
API docs at http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies with pnpm
pnpm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with API URL and Better Auth config

# Start development server
pnpm dev
```

Frontend will be available at http://localhost:3000

## Project Structure

```
phase-2/
├── backend/
│   ├── src/
│   │   ├── models/          # SQLModel entities (User, Task)
│   │   ├── services/        # Business logic
│   │   ├── api/             # FastAPI endpoints
│   │   ├── core/            # Configuration, security, database
│   │   └── middleware/      # Logging, CORS
│   ├── tests/               # pytest tests
│   ├── alembic/             # Database migrations
│   └── pyproject.toml       # uv dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Better Auth, API client
│   │   └── types/           # TypeScript interfaces
│   ├── public/              # Static assets
│   └── package.json         # pnpm dependencies
├── specs/                   # Feature specifications
│   └── 001-todo-app-baseline/
│       ├── spec.md          # Requirements
│       ├── plan.md          # Architecture
│       ├── tasks.md         # Implementation tasks
│       ├── data-model.md    # Database entities
│       ├── contracts/       # API contracts (OpenAPI)
│       └── quickstart.md    # Setup guide
└── .specify/                # Spec-Kit Plus
    ├── memory/
    │   └── constitution.md  # Development principles
    └── templates/           # Document templates
```

## Development

### Running Locally

1. Start backend: `cd backend && fastapi dev src/main.py`
2. Start frontend: `cd frontend && pnpm dev`
3. Access application at http://localhost:3000

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing

**Manual Testing:**
- See acceptance scenarios in `specs/001-todo-app-baseline/spec.md`
- Follow test procedures in `specs/001-todo-app-baseline/quickstart.md`

**Backend Tests:**
```bash
cd backend
pytest
```

## API Documentation

Once the backend is running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Security

- JWT tokens for authentication (expire after 24 hours)
- Bcrypt password hashing (cost factor 12)
- Multi-user isolation enforced at database and API layers
- HTTPS required in production
- No secrets in code (all via environment variables)

## Constitution & Principles

This project follows strict **Spec-Driven Development (SDD)** principles:

1. **Spec-First Development**: No code before approved specifications
2. **Single Code Authority**: Only Claude Code writes implementation
3. **Separation of Concerns**: Strict backend/frontend boundaries
4. **Authentication Enforcement**: JWT on all protected endpoints
5. **Database Persistence First**: PostgreSQL with SQLModel
6. **Observability**: Structured logging and error handling

See `.specify/memory/constitution.md` for complete governance rules.

## Documentation

- **Feature Specification**: `specs/001-todo-app-baseline/spec.md`
- **Implementation Plan**: `specs/001-todo-app-baseline/plan.md`
- **Task Breakdown**: `specs/001-todo-app-baseline/tasks.md`
- **Data Model**: `specs/001-todo-app-baseline/data-model.md`
- **API Contracts**: `specs/001-todo-app-baseline/contracts/api.yaml`
- **Setup Guide**: `specs/001-todo-app-baseline/quickstart.md`

## License

[Specify your license here]

## Contributing

This project uses Spec-Kit Plus for spec-driven development. All contributions must:
1. Start with a specification (`/sp.specify`)
2. Create an implementation plan (`/sp.plan`)
3. Generate tasks (`/sp.tasks`)
4. Only then implement (`/sp.implement`)

See `.specify/` for templates and guidelines.
