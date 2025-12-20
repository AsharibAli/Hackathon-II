# Data Model: Todo Full-Stack Web Application - Baseline

**Feature**: 001-todo-app-baseline
**Date**: 2025-12-18
**Purpose**: Define database entities, relationships, and validation rules

## Entity Overview

This application has **2 primary entities**:

1. **User**: Represents an authenticated person using the application
2. **Task**: Represents a single todo item belonging to a user

**Relationship**: One User has many Tasks (one-to-many)

## Entity: User

### Purpose
Stores authentication credentials and metadata for users who can create and manage personal todo lists.

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier for the user |
| `email` | String (255) | Unique, Not Null, Email format | User's email address for login |
| `hashed_password` | String (255) | Not Null | Bcrypt-hashed password (never store plaintext) |
| `created_at` | DateTime | Not Null, Default: now() | Timestamp when user account was created |
| `updated_at` | DateTime | Not Null, Default: now(), Auto-update | Timestamp of last account update |
| `is_active` | Boolean | Not Null, Default: true | Whether the account is active (for future soft delete) |

### Indexes

- **Primary Key**: `id`
- **Unique Index**: `email` (enforces email uniqueness, speeds up login queries)

### Relationships

- **tasks**: One-to-Many relationship with Task entity
  - Cascade delete: When a user is deleted, all their tasks are deleted

### Validation Rules (Application Layer)

From spec FR-002, FR-003:

- Email MUST be valid format (regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
- Password MUST be minimum 8 characters before hashing
- Email uniqueness enforced at database level (unique constraint)

### Security Notes

- Password MUST be hashed with bcrypt (cost factor 12) before storage
- NEVER return `hashed_password` in API responses
- JWT payload should contain `id` and `email` only (no sensitive data)

### SQLModel Implementation Reference

```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255, regex="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    is_active: bool = Field(default=True)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="owner", cascade_delete=True)
```

## Entity: Task

### Purpose
Stores individual todo items with title, description, and completion status, scoped to a specific user.

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier for the task |
| `user_id` | UUID | Foreign Key (users.id), Not Null, Indexed | Owner of this task (enforces multi-user isolation) |
| `title` | String (200) | Not Null | Task title (required) |
| `description` | String (2000) | Nullable | Optional detailed description |
| `is_completed` | Boolean | Not Null, Default: false | Whether task is marked as complete |
| `created_at` | DateTime | Not Null, Default: now() | Timestamp when task was created |
| `updated_at` | DateTime | Not Null, Default: now(), Auto-update | Timestamp of last task update |

### Indexes

- **Primary Key**: `id`
- **Foreign Key Index**: `user_id` (critical for multi-user isolation queries)
- **Composite Index**: `(user_id, created_at DESC)` (optimizes "get user's tasks ordered by newest first")

### Relationships

- **owner**: Many-to-One relationship with User entity
  - If user is deleted, all their tasks are deleted (cascade)

### Validation Rules (Application Layer)

From spec FR-017, FR-018, FR-019:

- Title MUST NOT be empty or null
- Title length MUST be ≤ 200 characters
- Description length MUST be ≤ 2000 characters (if provided)
- Title whitespace should be trimmed before validation

### Multi-User Isolation Rules

From spec FR-021, FR-022, FR-024:

- ALL queries MUST filter by `user_id`
- NEVER allow queries without user_id scope
- API endpoints MUST verify the authenticated user's ID matches the requested user_id
- Task IDs are globally unique (UUID) but MUST NOT be guessable

### Ordering

From spec FR-016:
- Default ordering: `created_at DESC` (newest tasks first)

### SQLModel Implementation Reference

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationships
    owner: User = Relationship(back_populates="tasks")
```

## Database Diagram

```
┌─────────────────────────────────────┐
│ User                                │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ email: String (UNIQUE, INDEXED)     │
│ hashed_password: String             │
│ created_at: DateTime                │
│ updated_at: DateTime                │
│ is_active: Boolean                  │
└─────────────────────────────────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────────────────────┐
│ Task                                │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ user_id: UUID (FK, INDEXED)         │
│ title: String(200)                  │
│ description: String(2000), NULL     │
│ is_completed: Boolean               │
│ created_at: DateTime                │
│ updated_at: DateTime                │
└─────────────────────────────────────┘

Indexes:
- users: (email) UNIQUE
- tasks: (user_id, created_at DESC) COMPOSITE
```

## State Transitions

### Task Completion State

```
┌─────────────┐           toggle            ┌─────────────┐
│             │ ──────────────────────────▶  │             │
│  Incomplete │                              │  Completed  │
│ (is_completed │ ◀──────────────────────────  │ (is_completed│
│   = false)  │           toggle            │   = true)   │
└─────────────┘                              └─────────────┘
       ▲                                              │
       │                                              │
       └───────────────── delete ─────────────────────┘
                       (permanent)
```

**Transitions**:
- **Create**: Task starts as `is_completed = false` (spec FR-009, acceptance scenario 3)
- **Toggle**: User can switch between completed/incomplete any number of times (spec FR-013)
- **Delete**: Permanent removal, no soft delete (spec assumption)

## Query Patterns

### Critical Query: Get User's Tasks (Multi-User Isolation)

```sql
-- SQL equivalent of required query pattern
SELECT * FROM tasks
WHERE user_id = :authenticated_user_id
ORDER BY created_at DESC;
```

**Security Rule**: NEVER execute a task query without `WHERE user_id = :authenticated_user_id`

### Get Single Task (with Authorization Check)

```sql
-- SQL equivalent
SELECT * FROM tasks
WHERE id = :task_id AND user_id = :authenticated_user_id;
```

**Security Rule**: Even with task ID, MUST verify user_id matches authenticated user

### Create Task

```sql
INSERT INTO tasks (id, user_id, title, description, is_completed, created_at, updated_at)
VALUES (uuid_generate_v4(), :authenticated_user_id, :title, :description, false, NOW(), NOW());
```

**Security Rule**: `user_id` MUST be set from authenticated user, NEVER from client input

## Migration Strategy

### Initial Migration (001_create_users_and_tasks.py)

**Up**:
1. Create `users` table with all fields and constraints
2. Create unique index on `users.email`
3. Create `tasks` table with all fields and constraints
4. Create foreign key constraint `tasks.user_id → users.id` with CASCADE DELETE
5. Create index on `tasks.user_id`
6. Create composite index on `tasks (user_id, created_at DESC)`

**Down**:
1. Drop `tasks` table (cascade drops foreign key and indexes)
2. Drop `users` table (cascade drops indexes)

### Future Migrations (if needed)

- Adding indexes for performance
- Adding fields (e.g., `task.priority`, `task.due_date`)
- Adding tables (e.g., `tags`, `categories`)

## Data Integrity Rules

### Enforced by Database

- Email uniqueness (unique constraint)
- User-Task relationship (foreign key constraint)
- Cascade delete (delete user → delete all their tasks)
- Non-null constraints on required fields

### Enforced by Application

- Email format validation
- Password minimum length
- Task title/description length limits
- User ID scoping on all queries
- Authorization checks (task belongs to user)

## Test Data Scenarios

For manual testing per acceptance scenarios:

**User 1**:
- Email: `user1@example.com`
- Password: `password123`
- Tasks: 3 tasks (2 incomplete, 1 complete)

**User 2**:
- Email: `user2@example.com`
- Password: `password456`
- Tasks: 2 tasks (both incomplete)

**Edge Cases to Test**:
- User with 0 tasks (empty state)
- User with 100+ tasks (performance)
- Task with maximum length title (200 chars)
- Task with maximum length description (2000 chars)
- Task with no description (null)

## Summary

This data model supports all specification requirements:

- ✅ Multi-user isolation via `user_id` scoping (FR-011, FR-021, FR-022, FR-024)
- ✅ Task CRUD operations (FR-009, FR-012, FR-013, FR-014, FR-015)
- ✅ Data validation (FR-017, FR-018, FR-019)
- ✅ Authentication support (FR-001 through FR-008)
- ✅ Performance constraints (indexed queries, SC-003, SC-006)
- ✅ Data persistence (FR-015, SC-007)

Ready to generate API contracts (next step).
