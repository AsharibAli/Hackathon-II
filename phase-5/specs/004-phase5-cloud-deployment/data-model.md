# Data Model: Phase 5 Advanced Cloud Deployment

**Feature**: 004-phase5-cloud-deployment
**Date**: 2025-12-25
**Status**: Complete

## Entity Overview

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │───1:N─│    Task     │───N:M─│    Tag      │
└─────────────┘       └─────────────┘       └─────────────┘
                            │
                            │ 1:N (self-reference)
                            ▼
                      ┌─────────────┐
                      │    Task     │ (child/recurring instance)
                      └─────────────┘
```

---

## E-001: Task (Extended)

### Description
Core entity representing a todo item. Extended from Phase 4 with priority, tags, due dates, reminders, and recurrence support.

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique identifier |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Optional detailed description |
| is_completed | BOOLEAN | DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp (UTC) |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp (UTC) |
| user_id | VARCHAR(100) | NOT NULL, INDEX | Owner user ID from JWT |
| priority | VARCHAR(10) | DEFAULT 'medium' | low, medium, high |
| due_date | TIMESTAMP | NULLABLE | Optional due date (UTC) |
| remind_at | TIMESTAMP | NULLABLE | Scheduled reminder time (UTC) |
| reminder_sent | BOOLEAN | DEFAULT FALSE | Whether reminder was sent |
| recurrence | VARCHAR(10) | DEFAULT 'none' | none, daily, weekly, monthly |
| parent_task_id | INTEGER | FK → tasks.id, NULLABLE | Link to parent recurring task |

### Indexes

| Index Name | Columns | Type |
|------------|---------|------|
| idx_tasks_user | user_id | B-tree |
| idx_tasks_priority | priority | B-tree |
| idx_tasks_due_date | due_date | B-tree |
| idx_tasks_reminder | remind_at, reminder_sent | Composite B-tree |
| idx_tasks_parent | parent_task_id | B-tree |

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Recurrence(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(max_length=100, nullable=False, index=True)

    # Phase 5 additions
    priority: Priority = Field(default=Priority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None, index=True)
    remind_at: Optional[datetime] = Field(default=None)
    reminder_sent: bool = Field(default=False)
    recurrence: Recurrence = Field(default=Recurrence.NONE)
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")

    # Relationships
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model="TaskTag")
    parent_task: Optional["Task"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
```

### State Transitions

```
┌─────────────┐    complete     ┌─────────────┐
│   Pending   │────────────────▶│  Completed  │
│is_completed │                 │is_completed │
│   = false   │◀────────────────│   = true    │
└─────────────┘    uncomplete   └─────────────┘
       │
       │ set reminder
       ▼
┌─────────────┐    reminder     ┌─────────────┐
│Has Reminder │────fired───────▶│Reminder Sent│
│remind_at set│                 │reminder_sent│
│reminder_sent│                 │   = true    │
│  = false    │                 └─────────────┘
└─────────────┘
```

### Validation Rules

1. **Title**: Required, 1-255 characters
2. **Priority**: Must be one of: low, medium, high
3. **Recurrence**: Must be one of: none, daily, weekly, monthly
4. **Due Date**: If set, must be a valid datetime
5. **Remind At**: If set, must be before or equal to due_date
6. **Parent Task ID**: If set, must reference existing task with same user_id

---

## E-002: Tag

### Description
Represents a label for task categorization. Tags are case-insensitive (stored lowercase).

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique identifier |
| name | VARCHAR(50) | NOT NULL, UNIQUE | Tag name (lowercase) |
| user_id | VARCHAR(100) | NOT NULL | Owner user ID |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

### Indexes

| Index Name | Columns | Type |
|------------|---------|------|
| idx_tags_name_user | name, user_id | Unique composite |

### SQLModel Definition

```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, nullable=False)
    user_id: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="tags", link_model="TaskTag")

    class Config:
        # Ensure name is stored lowercase
        @validator('name', pre=True)
        def lowercase_name(cls, v):
            return v.lower() if v else v
```

### Validation Rules

1. **Name**: Required, 1-50 characters, stored lowercase
2. **Unique per user**: Same tag name cannot exist twice for same user

---

## E-003: TaskTag (Junction)

### Description
Many-to-many relationship between Task and Tag.

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| task_id | INTEGER | PK, FK → tasks.id | Reference to task |
| tag_id | INTEGER | PK, FK → tags.id | Reference to tag |

### SQLModel Definition

```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
```

---

## E-004: TaskEvent (Kafka Message)

### Description
Event published to Kafka when task state changes. Not persisted in database.

### Schema (JSON)

```json
{
  "event_type": "task.created | task.updated | task.completed | task.deleted",
  "task_id": 123,
  "task_data": {
    "id": 123,
    "title": "Task title",
    "description": "Optional description",
    "is_completed": false,
    "priority": "high",
    "due_date": "2025-01-15T14:00:00Z",
    "remind_at": "2025-01-15T13:00:00Z",
    "recurrence": "weekly",
    "parent_task_id": null,
    "tags": ["work", "urgent"],
    "created_at": "2025-01-10T10:00:00Z",
    "updated_at": "2025-01-10T10:00:00Z"
  },
  "user_id": "user-123",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Pydantic Model

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaskData(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    priority: str
    due_date: Optional[datetime]
    remind_at: Optional[datetime]
    recurrence: str
    parent_task_id: Optional[int]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class TaskEvent(BaseModel):
    event_type: str  # task.created, task.updated, task.completed, task.deleted
    task_id: int
    task_data: TaskData
    user_id: str
    timestamp: datetime
```

---

## E-005: ReminderEvent (Kafka Message)

### Description
Event published to Kafka when a reminder is due. Consumed by notification-service.

### Schema (JSON)

```json
{
  "task_id": 123,
  "title": "Submit report",
  "due_at": "2025-01-15T14:00:00Z",
  "remind_at": "2025-01-15T13:00:00Z",
  "user_id": "user-123"
}
```

### Pydantic Model

```python
class ReminderEvent(BaseModel):
    task_id: int
    title: str
    due_at: datetime
    remind_at: datetime
    user_id: str
```

---

## Migration Plan

### Migration 001: Add Phase 5 Columns

```sql
-- Up migration
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP;
ALTER TABLE tasks ADD COLUMN remind_at TIMESTAMP;
ALTER TABLE tasks ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN recurrence VARCHAR(10) DEFAULT 'none';
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id);

CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_reminder ON tasks(remind_at, reminder_sent);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);

-- Down migration
DROP INDEX IF EXISTS idx_tasks_parent;
DROP INDEX IF EXISTS idx_tasks_reminder;
DROP INDEX IF EXISTS idx_tasks_due_date;
DROP INDEX IF EXISTS idx_tasks_priority;

ALTER TABLE tasks DROP COLUMN IF EXISTS parent_task_id;
ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence;
ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_sent;
ALTER TABLE tasks DROP COLUMN IF EXISTS remind_at;
ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;
ALTER TABLE tasks DROP COLUMN IF EXISTS priority;
```

### Migration 002: Create Tags Tables

```sql
-- Up migration
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_tags_name_user ON tags(name, user_id);

CREATE TABLE task_tags (
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

-- Down migration
DROP TABLE IF EXISTS task_tags;
DROP TABLE IF EXISTS tags;
```

---

## Query Patterns

### Filter Tasks by Priority
```sql
SELECT * FROM tasks
WHERE user_id = :user_id
  AND priority = :priority
  AND is_completed = :completed
ORDER BY created_at DESC;
```

### Filter Tasks by Tag
```sql
SELECT t.* FROM tasks t
JOIN task_tags tt ON t.id = tt.task_id
JOIN tags tg ON tt.tag_id = tg.id
WHERE t.user_id = :user_id
  AND tg.name = LOWER(:tag_name);
```

### Find Overdue Tasks
```sql
SELECT * FROM tasks
WHERE user_id = :user_id
  AND due_date < NOW()
  AND is_completed = FALSE
ORDER BY due_date ASC;
```

### Find Pending Reminders
```sql
SELECT * FROM tasks
WHERE remind_at <= NOW()
  AND reminder_sent = FALSE
  AND is_completed = FALSE;
```

### Search Tasks
```sql
SELECT * FROM tasks
WHERE user_id = :user_id
  AND (
    LOWER(title) LIKE LOWER(:query)
    OR LOWER(description) LIKE LOWER(:query)
  )
ORDER BY created_at DESC;
```
