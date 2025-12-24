# Data Model: Combined CUI & GUI Todo Application

**Feature Branch**: `003-combined-cui-gui`
**Date**: 2025-12-23
**Spec**: [spec.md](./spec.md)

## Overview

The Combined CUI & GUI feature **does not require any database schema changes**. This integration leverages the existing data models from Phase-2 (Tasks) and Phase-3 (Conversations/Messages).

Both CUI and GUI interfaces operate on the **same underlying data**, ensuring consistency across modes.

## Existing Entities (No Changes)

### Entity: User

Represents an authenticated person using the application. Both CUI and GUI modes share the same user authentication.

```text
User
├── id: UUID (Primary Key)
├── email: String(255) [UNIQUE, INDEXED]
├── hashed_password: String(255)
├── full_name: String(100) [NULLABLE]
├── profile_picture: String(500) [NULLABLE]
├── is_active: Boolean (default: True)
├── created_at: DateTime (auto-set on creation)
├── updated_at: DateTime (auto-set, updates on change)
└── Relationships:
    ├── tasks: One-to-Many → Task
    └── conversations: One-to-Many → Conversation
```

### Entity: Task

Represents a todo item. **Accessible and modifiable via both CUI and GUI modes**.

```text
Task
├── id: UUID (Primary Key)
├── user_id: UUID [FOREIGN KEY → users.id, INDEXED]
├── title: String(200) [NOT NULL]
├── description: String(2000) [NULLABLE]
├── is_completed: Boolean (default: False)
├── created_at: DateTime (auto-set on creation)
├── updated_at: DateTime (auto-set, updates on change)
└── Relationship:
    └── owner: Many-to-One → User
```

**Access Patterns:**
- **GUI Mode**: Direct CRUD via `/api/tasks` endpoints
- **CUI Mode**: Indirect via MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)

### Entity: Conversation

Represents a chat session for CUI mode. **Only used by CUI mode**.

```text
Conversation
├── id: UUID (Primary Key)
├── user_id: UUID [FOREIGN KEY → users.id, INDEXED]
├── title: String(100) [NULLABLE] (auto-generated from first message)
├── created_at: DateTime (auto-set on creation)
├── updated_at: DateTime (auto-set, updates on change)
└── Relationships:
    ├── user: Many-to-One → User
    └── messages: One-to-Many → Message (cascade delete)
```

### Entity: Message

Represents a single message in a conversation. **Only used by CUI mode**.

```text
Message
├── id: UUID (Primary Key)
├── conversation_id: UUID [FOREIGN KEY → conversations.id, INDEXED]
├── role: String ('user' | 'assistant')
├── content: String(10000)
├── created_at: DateTime (auto-set on creation)
└── Relationship:
    └── conversation: Many-to-One → Conversation
```

## Entity Relationship Diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE                                 │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────┐          ┌──────────┐          ┌──────────────┐
    │   User   │ 1──────N │   Task   │          │ Conversation │
    │          │          │          │          │              │
    │ • id     │          │ • id     │          │ • id         │
    │ • email  │          │ • user_id│          │ • user_id    │
    │ • ...    │          │ • title  │          │ • title      │
    └──────────┘          │ • ...    │          │ • ...        │
         │                └──────────┘          └──────────────┘
         │                     ▲                       │
         │                     │                       │ 1
         │                     │                       │
         │      ┌──────────────┴──────────────┐       │
         │      │                             │       │
         │      │       GUI MODE              │       N
         │      │   (TaskList, TaskForm)      │       │
         │      │                             │       │
         │      └─────────────────────────────┘       │
         │                                            │
         │ 1                                    ┌──────────┐
         │                                      │ Message  │
         └──────────────────────────────────────│          │
                        │                       │ • id     │
                        │                       │ • conv_id│
              ┌─────────┴─────────┐             │ • role   │
              │                   │             │ • content│
              │    CUI MODE       │             └──────────┘
              │  (ChatInterface)  │                  │
              │                   │                  │
              └───────────────────┘                  │
                        │                           │
                        │ MCP Tools                 │
                        └───────────────────────────┘
                              ▲
                              │
                        Uses Task API
```

## Data Flow Between Modes

### GUI Mode Data Flow

```text
User Action (GUI)
    │
    ▼
┌─────────────────┐
│ React Component │ (TaskList, TaskForm, etc.)
│   • TaskList    │
│   • TaskForm    │
│   • TaskItem    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   api.ts        │ (Frontend API client)
│ • getTasks()    │
│ • createTask()  │
│ • updateTask()  │
│ • deleteTask()  │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│ Backend API     │
│ /api/tasks/*    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   (Tasks table) │
└─────────────────┘
```

### CUI Mode Data Flow

```text
User Message (CUI)
    │
    ▼
┌─────────────────┐
│ ChatInterface   │
│   • ChatInput   │
│   • ChatMessage │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   api.ts        │
│ • sendMessage() │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│ Backend API     │
│ POST /api/chat  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Agent      │ (OpenAI + MCP Tools)
│   • Interprets  │
│   • Invokes tool│
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   MCP Tools     │────▶│   Tasks Service │
│ • add_task      │     │ (Same as GUI!)  │
│ • list_tasks    │     └────────┬────────┘
│ • complete_task │              │
│ • update_task   │              ▼
│ • delete_task   │     ┌─────────────────┐
└─────────────────┘     │   Database      │
                        │   (Tasks table) │
                        └─────────────────┘
```

### Data Synchronization

Since both modes use the **same database tables** and **same backend services**, data is automatically synchronized:

1. **Task created via GUI** → Appears in CUI when user asks "Show my tasks"
2. **Task created via CUI** → Appears in GUI when TaskList is rendered
3. **Task completed via GUI** → CUI reports correct status
4. **Task deleted via CUI** → Disappears from GUI TaskList

**No special sync mechanism required** - just refresh data on mode switch.

## Query Patterns

### GUI Mode Queries

| Operation | Service Method | SQL Pattern |
|-----------|---------------|-------------|
| List tasks | `TasksService.get_user_tasks(user_id)` | `SELECT * FROM tasks WHERE user_id = ?` |
| Create task | `TasksService.create_task(user_id, data)` | `INSERT INTO tasks ...` |
| Update task | `TasksService.update_task(user_id, task_id, data)` | `UPDATE tasks SET ... WHERE id = ? AND user_id = ?` |
| Delete task | `TasksService.delete_task(user_id, task_id)` | `DELETE FROM tasks WHERE id = ? AND user_id = ?` |
| Toggle complete | `TasksService.toggle_complete(user_id, task_id)` | `UPDATE tasks SET is_completed = NOT is_completed ...` |

### CUI Mode Queries

| MCP Tool | Service Method | SQL Pattern |
|----------|---------------|-------------|
| add_task | `TasksService.create_task(user_id, data)` | `INSERT INTO tasks ...` |
| list_tasks | `TasksService.get_user_tasks(user_id, completed?)` | `SELECT * FROM tasks WHERE user_id = ? [AND is_completed = ?]` |
| complete_task | `TasksService.mark_complete(user_id, task_id)` | `UPDATE tasks SET is_completed = true ...` |
| update_task | `TasksService.update_task(user_id, task_id, data)` | `UPDATE tasks SET ... WHERE id = ? AND user_id = ?` |
| delete_task | `TasksService.delete_task(user_id, task_id)` | `DELETE FROM tasks WHERE id = ? AND user_id = ?` |

## Migration Status

**No migrations required for Phase-4.**

All necessary tables exist from previous phases:
- `users` (Phase-2)
- `tasks` (Phase-2)
- `conversations` (Phase-3)
- `messages` (Phase-3)

## Summary

The Combined CUI & GUI feature is a **frontend integration project**. The data model remains unchanged, and both interfaces operate on the same underlying data through shared backend services. This ensures:

1. **Data Consistency** - Same database, same services
2. **No Schema Changes** - Zero migration risk
3. **Simplified Architecture** - No data synchronization complexity
4. **Unified User Experience** - Tasks are always up-to-date regardless of mode
