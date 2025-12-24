# Research: Todo Full-Stack Web Application - Baseline

**Feature**: 001-todo-app-baseline
**Date**: 2025-12-18
**Purpose**: Document technology choices, patterns, and best practices for implementation

## Authentication & JWT Implementation

### Decision: Better Auth (Frontend) + python-jose (Backend)

**Rationale**:
- Better Auth provides production-ready authentication for Next.js with minimal configuration
- Supports JWT tokens natively, aligning with constitutional requirements
- Backend uses python-jose for JWT verification (widely adopted, secure, well-maintained)
- Clear separation: Frontend issues tokens via Better Auth, Backend verifies and extracts user identity

**Implementation Pattern**:
```
1. User registers/logs in via Better Auth on frontend
2. Better Auth issues JWT containing user_id, email, expiration
3. Frontend stores JWT (httpOnly cookie or localStorage)
4. Frontend includes JWT in Authorization: Bearer <token> header for API calls
5. Backend middleware verifies JWT signature using shared secret
6. Backend extracts user_id from verified token claims
7. Backend scopes all database queries using extracted user_id
```

**Alternatives Considered**:
- **OAuth2 with external provider**: Rejected - adds external dependency, spec requires email/password
- **Session-based auth**: Rejected - requires shared state between frontend/backend, JWT stateless approach simpler for API
- **Auth0/Clerk**: Rejected - introduces vendor lock-in, Better Auth is open-source and self-hosted

**Security Considerations**:
- JWT secret MUST be strong (32+ random characters) and stored in environment variables
- Token expiration set to 24 hours (configurable via environment variable)
- HTTPS required in production to prevent token interception
- Passwords hashed with bcrypt (cost factor 12)

## SQLModel ORM Best Practices

### Decision: SQLModel with Alembic Migrations

**Rationale**:
- SQLModel combines SQLAlchemy + Pydantic, providing both ORM and validation
- Type-safe: TypeScript-like experience in Python with full IDE support
- Constitutional requirement (Principle VI)
- Alembic handles database schema versioning and migrations

**Model Design Pattern**:
```python
# Base pattern for all models
class EntityBase(SQLModel):
    # Shared create/update fields

class Entity(EntityBase, table=True):
    # DB table fields with __tablename__

class EntityCreate(EntityBase):
    # API request schema (no id, timestamps)

class EntityRead(EntityBase):
    # API response schema (includes id, timestamps)

class EntityUpdate(SQLModel):
    # API update schema (all fields optional)
```

**Relationship Pattern (User → Tasks)**:
```python
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    owner: User = Relationship(back_populates="tasks")
```

**Query Scoping Pattern (Multi-User Isolation)**:
```python
# ALWAYS filter by user_id - NEVER expose queries without this filter
def get_user_tasks(session: Session, user_id: UUID):
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
```

**Alternatives Considered**:
- **Raw SQLAlchemy**: Rejected - SQLModel provides better type safety and less boilerplate
- **Tortoise ORM**: Rejected - less mature, smaller community
- **Django ORM**: Rejected - requires Django framework, we're using FastAPI

## FastAPI Project Structure

### Decision: Layered Architecture (Models → Services → API → Dependencies)

**Rationale**:
- Clear separation of concerns (data, business logic, API endpoints, cross-cutting)
- Testable: Each layer can be tested independently
- Scalable: Easy to add new endpoints, services, models
- Aligns with FastAPI best practices from official documentation

**Dependency Injection Pattern**:
```python
# api/deps.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    # Verify JWT, extract user_id, fetch user from DB
    # Raise HTTPException if invalid

# api/tasks.py
@router.get("/tasks")
def get_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # current_user automatically injected and validated
    return tasks_service.get_user_tasks(session, current_user.id)
```

**Error Handling Pattern**:
```python
# Centralized exception handler
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": exc.error_type}
    )
```

**Alternatives Considered**:
- **Flat structure (all in main.py)**: Rejected - doesn't scale, hard to test
- **Domain-driven design**: Rejected - overkill for this scope (2 entities)

## Next.js App Router Best Practices

### Decision: Server Components + Client Components Pattern

**Rationale**:
- App Router is the recommended approach for Next.js 14+
- Server Components reduce client bundle size
- Client Components used only for interactivity (forms, buttons)
- Built-in support for loading states, error boundaries

**Layout Pattern**:
```
app/
├── layout.tsx              # Root layout (auth provider)
├── page.tsx                # Landing page (redirect based on auth)
├── (auth)/                 # Auth routes (login, register)
│   ├── layout.tsx
│   ├── login/page.tsx
│   └── register/page.tsx
└── (app)/                  # Protected app routes
    ├── layout.tsx          # Verify auth, redirect if not logged in
    └── page.tsx            # Main todo list
```

**Data Fetching Pattern**:
```typescript
// Server Component (default)
async function TaskList() {
  const tasks = await fetch(`${API_URL}/tasks`, {
    headers: { Authorization: `Bearer ${getToken()}` }
  })
  return <TaskListClient tasks={tasks} />
}

// Client Component (interactive)
'use client'
function TaskListClient({ tasks }) {
  const [localTasks, setLocalTasks] = useState(tasks)
  // Handle mutations, optimistic updates
}
```

**Alternatives Considered**:
- **Pages Router**: Rejected - App Router is the future, better DX
- **Client-side only (SPA)**: Rejected - worse SEO, slower initial load

## shadcn/ui Component Strategy

### Decision: Install Only Needed Components

**Rationale**:
- shadcn/ui uses "copy component to project" approach, not npm package
- Keeps bundle size minimal
- Full customization control
- Uses Radix UI primitives (accessibility built-in)

**Components Needed**:
- Button (create, edit, delete, toggle actions)
- Input (task title, description, email, password)
- Card (task items)
- Form (Better Auth integration)
- Dialog (delete confirmation)
- Checkbox (task completion toggle)
- Label, Toast (feedback)

**Styling Approach**:
- Tailwind CSS for all styling (no CSS modules, no styled-components)
- Use shadcn/ui default theme, customize via tailwind.config.ts
- Mobile-first responsive design

**Alternatives Considered**:
- **Material-UI (MUI)**: Rejected - heavier bundle, less customization
- **Chakra UI**: Rejected - different styling approach, not as lightweight
- **Headless UI**: Rejected - shadcn/ui is built on similar primitives (Radix) with better DX

## Database Connection & Pooling

### Decision: Neon Serverless PostgreSQL with psycopg2/asyncpg

**Rationale**:
- Neon provides serverless PostgreSQL with built-in connection pooling
- No infrastructure management required
- Scales automatically with load
- Compatible with standard PostgreSQL drivers

**Connection Pattern**:
```python
# Sync mode (SQLModel default)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,
    max_overflow=10
)

# Alternative: Async mode (for high concurrency)
# Requires asyncpg + SQLModel async support
```

**Migration Strategy**:
```bash
# Initialize Alembic
alembic init alembic

# Generate migration from SQLModel changes
alembic revision --autogenerate -m "Create user and task tables"

# Apply migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Alternatives Considered**:
- **Self-hosted PostgreSQL**: Rejected - requires infrastructure management
- **PlanetScale (MySQL)**: Rejected - spec requires PostgreSQL
- **Supabase**: Rejected - includes extra features not needed, prefer simpler Neon

## Environment Configuration

### Decision: Pydantic BaseSettings (Backend) + next.config.js (Frontend)

**Rationale**:
- Pydantic BaseSettings provides type-safe environment variable validation
- Fails fast if required variables missing
- Supports .env files for local development

**Backend Configuration**:
```python
# core/config.py
class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    JWT_SECRET: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True
```

**Frontend Configuration**:
```typescript
// next.config.js
module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
}
```

**Required Environment Variables**:

Backend (`.env`):
```
DATABASE_URL=postgresql://user:pass@host/dbname
JWT_SECRET=<32+ character random string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=http://localhost:3000,https://production-domain.com
```

Frontend (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<random string>
BETTER_AUTH_URL=http://localhost:3000
```

**Alternatives Considered**:
- **dotenv only**: Rejected - no validation, typos cause runtime errors
- **Config files (YAML/JSON)**: Rejected - environment variables are standard for 12-factor apps

## Testing Strategy

### Decision: Manual E2E Testing per Acceptance Scenarios

**Rationale**:
- Specification doesn't require automated tests (Principle V)
- Each user story has clear acceptance scenarios for manual testing
- Manual testing sufficient for baseline MVP
- Can add automated tests later if needed

**Testing Checklist** (maps to spec acceptance scenarios):

**P1 - Authentication**:
- [ ] Register new user with valid email/password
- [ ] Login with valid credentials, receive JWT
- [ ] Access protected endpoint without token → 401
- [ ] Logout and verify session terminated

**P2 - View Tasks**:
- [ ] Login as User A, create tasks, verify visible
- [ ] Login as User B, verify User A's tasks NOT visible
- [ ] Refresh page, verify tasks persist

**P3 - Create Tasks**:
- [ ] Create task with title only
- [ ] Create task with title + description
- [ ] Attempt to create task without title → validation error

**P4 - Toggle Completion**:
- [ ] Toggle task from incomplete to complete
- [ ] Toggle task from complete to incomplete
- [ ] Refresh page, verify completion status persists

**P5 - Update Tasks**:
- [ ] Edit task title, verify saved
- [ ] Edit task description, verify saved
- [ ] Cancel edit, verify no changes
- [ ] Attempt to save empty title → validation error

**P6 - Delete Tasks**:
- [ ] Delete task, confirm deletion prompt
- [ ] Confirm deletion, verify task removed
- [ ] Cancel deletion, verify task remains

**Future: Automated Testing** (if requested):
- Backend: pytest + FastAPI TestClient for endpoint tests
- Frontend: Vitest + React Testing Library for component tests
- E2E: Playwright for full user journey tests

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Auth** | Better Auth + python-jose JWT | Frontend: prod-ready Next.js auth. Backend: secure JWT verification |
| **ORM** | SQLModel + Alembic | Type-safe, Pydantic integration, constitutional requirement |
| **Backend Structure** | Layered (Models/Services/API/Deps) | Testable, scalable, clear separation |
| **Frontend Structure** | App Router + Server/Client Components | Modern Next.js, optimal performance |
| **UI Components** | shadcn/ui + Tailwind CSS | Lightweight, customizable, accessible |
| **Database** | Neon Serverless PostgreSQL | Managed, scalable, PostgreSQL-compatible |
| **Config** | Pydantic BaseSettings + env vars | Type-safe, validated, 12-factor app pattern |
| **Testing** | Manual E2E per acceptance scenarios | Spec doesn't require automation, MVP sufficient |

All decisions align with constitutional constraints and specification requirements. Ready to proceed to Phase 1 (data models and contracts).
