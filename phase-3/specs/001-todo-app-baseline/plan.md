# Implementation Plan: Todo Full-Stack Web Application - Baseline

**Branch**: `001-todo-app-baseline` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-app-baseline/spec.md`

## Summary

Build a multi-user Todo application with authentication and complete CRUD operations for tasks. The application will use a monorepo structure with separate frontend (Next.js + TypeScript) and backend (FastAPI + Python) applications. JWT-based authentication ensures multi-user isolation, with all task data scoped to the authenticated user. Database persistence via Neon PostgreSQL with SQLModel ORM ensures data durability and supports concurrent users.

**Primary Requirement**: Secure, multi-user task management system with registration, login, and full CRUD operations on tasks.

**Technical Approach**: Monorepo with strict separation between frontend and backend. Better Auth handles authentication on frontend with JWT tokens. Backend validates tokens and enforces user-scoped database queries. SQLModel provides type-safe ORM layer over PostgreSQL.

## Technical Context

**Language/Version**:
- Backend: Python 3.11+
- Frontend: TypeScript 5.x (strict mode)

**Primary Dependencies**:
- Backend: FastAPI 0.104+, SQLModel 0.0.14+, python-jose (JWT), passlib (bcrypt), Neon PostgreSQL driver
- Frontend: Next.js 14+ (App Router), Better Auth with JWT plugin, Tailwind CSS 3.x, shadcn/ui components

**Storage**: Neon Serverless PostgreSQL (cloud-hosted, connection pooling enabled)

**Testing**:
- Backend: pytest with FastAPI TestClient
- Frontend: Vitest + React Testing Library (for component tests if needed)
- Integration: Manual end-to-end testing per user story acceptance scenarios

**Target Platform**:
- Backend: Linux/Windows server (Python runtime)
- Frontend: Modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
- Deployment: Web application accessible via HTTPS

**Project Type**: Web application (frontend + backend monorepo)

**Performance Goals**:
- API response time <1 second for CRUD operations (SC-003)
- Login + view task list <3 seconds (SC-002)
- Support 100 concurrent users without degradation (SC-006)

**Constraints**:
- JWT tokens expire after 24 hours (configurable)
- Task title max 200 characters, description max 2000 characters
- Email uniqueness enforced at database level
- Password minimum 8 characters
- All database queries MUST be scoped to authenticated user ID
- No hardcoded secrets - all credentials via environment variables

**Scale/Scope**:
- 100+ tasks per user supported (SC-009)
- 100+ concurrent users (SC-006)
- 6 user stories (P1-P6) with independent implementation capability
- 2 entities (User, Task) with clear relationships

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-First Development ✅
- **Status**: PASS
- **Evidence**: Complete specification approved before planning. All 6 user stories defined with acceptance criteria. 24 functional requirements documented.

### Principle II: Single Code Authority ✅
- **Status**: PASS
- **Evidence**: No code written yet. Plan will guide Claude Code implementation only.

### Principle III: Separation of Concerns ✅
- **Status**: PASS
- **Evidence**: Monorepo structure with `backend/` and `frontend/` directories. Backend handles auth, database, API. Frontend handles UI, Better Auth integration, API client. No mixing planned.

### Principle IV: Authentication & Authorization Enforcement ✅
- **Status**: PASS
- **Evidence**:
  - FR-005: JWT token verification on all protected endpoints
  - FR-006: User identity extraction from tokens
  - FR-007: Access denial for invalid/missing tokens
  - FR-021: All database queries scoped to authenticated user ID
  - FR-022: Mismatched user ID requests rejected
  - FR-024: No information leakage about other users' tasks

### Principle V: Test-First When Specified ✅
- **Status**: PASS
- **Evidence**: Specification does not explicitly request test generation. Testing will be manual based on acceptance scenarios (SC-010). If tests requested later, will follow TDD workflow.

### Principle VI: Database Persistence First ✅
- **Status**: PASS
- **Evidence**:
  - FR-015: All task data persisted in database
  - SQLModel ORM mandated by constitution
  - Neon PostgreSQL specified
  - Migrations will be version-controlled (Alembic)
  - No in-memory-only storage

### Principle VII: Observability & Debuggability ✅
- **Status**: PASS
- **Evidence**: Plan includes structured logging at appropriate levels, error responses with context (FR-020), FastAPI built-in request correlation support.

### Architectural Constraints Compliance ✅

**Monorepo Structure**: ✅
- `backend/` and `frontend/` top-level directories
- `specs/` for shared specifications
- `.specify/memory/` for governance

**Frontend Stack**: ✅
- Next.js with App Router: Specified
- TypeScript strict mode: Will be configured in tsconfig.json
- Tailwind CSS: Specified
- shadcn/ui: Specified
- pnpm: Will be package manager

**Backend Stack**: ✅
- FastAPI (Python 3.11+): Specified
- SQLModel: Specified
- Neon Serverless PostgreSQL: Specified
- Better Auth with JWT: Specified (frontend integration)
- uv: Will be package manager

**Constraint Validations**:
- ✅ TypeScript strict mode will be enabled in `tsconfig.json`
- ✅ FastAPI app will configure CORS, auth middleware, exception handlers
- ✅ SQLModel models will use type annotations and relationships
- ✅ Better Auth will use JWT secret from environment variables
- ✅ Neon connection string will be in `.env` (gitignored)

### Summary: ALL GATES PASS ✅

No constitutional violations. Ready to proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-app-baseline/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (authentication patterns, SQLModel best practices)
├── data-model.md        # Phase 1 output (User and Task entities)
├── quickstart.md        # Phase 1 output (development setup, running the app)
├── contracts/           # Phase 1 output (API endpoint specifications)
│   └── api.yaml         # OpenAPI 3.0 spec for REST endpoints
└── checklists/          # Existing from /sp.specify
    └── requirements.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py          # User SQLModel
│   │   └── task.py          # Task SQLModel
│   ├── services/
│   │   ├── auth.py          # JWT verification, user extraction
│   │   └── tasks.py         # Task CRUD business logic
│   ├── api/
│   │   ├── deps.py          # Dependency injection (get_current_user)
│   │   ├── auth.py          # Auth endpoints (register, login, logout)
│   │   └── tasks.py         # Task CRUD endpoints
│   ├── core/
│   │   ├── config.py        # Settings (Pydantic BaseSettings)
│   │   ├── security.py      # Password hashing, JWT utilities
│   │   └── database.py      # SQLModel engine, session management
│   ├── middleware/
│   │   └── logging.py       # Structured logging middleware
│   └── main.py              # FastAPI app initialization
├── tests/
│   ├── conftest.py          # Pytest fixtures (test DB, test client)
│   ├── test_auth.py         # Auth endpoint tests
│   └── test_tasks.py        # Task endpoint tests
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini
├── pyproject.toml           # uv configuration
├── .env.example             # Example environment variables
└── README.md

frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── (app)/
│   │   │   └── page.tsx     # Main todo list page (protected)
│   │   ├── layout.tsx
│   │   └── page.tsx         # Landing/redirect
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── TaskList.tsx     # Task list display
│   │   ├── TaskItem.tsx     # Individual task item
│   │   ├── TaskForm.tsx     # Create/edit task form
│   │   └── AuthForm.tsx     # Login/register form
│   ├── lib/
│   │   ├── auth.ts          # Better Auth configuration
│   │   ├── api-client.ts    # Authenticated API client (fetch wrapper)
│   │   └── utils.ts         # Common utilities
│   └── types/
│       └── task.ts          # TypeScript interfaces for Task
├── public/
├── tests/                   # Vitest tests (if needed)
├── tailwind.config.ts
├── tsconfig.json            # Strict mode enabled
├── next.config.js
├── package.json             # pnpm workspace
├── .env.local.example
└── README.md

Root-level files:
├── .specify/                # Spec-Kit Plus configuration
│   ├── memory/
│   │   └── constitution.md
│   ├── scripts/
│   └── templates/
├── specs/                   # Feature specifications
│   └── 001-todo-app-baseline/
├── history/                 # Prompt history records
├── .gitignore               # Ignore .env, node_modules, __pycache__, etc.
├── docker-compose.yml       # Optional: local PostgreSQL + services
├── README.md                # Project overview
└── pnpm-workspace.yaml      # pnpm monorepo configuration
```

**Structure Decision**: Selected Web application (Option 2) structure due to separate frontend and backend requirements. This aligns with Constitution Principle III (Separation of Concerns) and enables independent development, testing, and deployment of each layer.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitutional requirements satisfied.
