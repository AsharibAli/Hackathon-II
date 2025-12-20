# MCP Tools Specification: Todo AI Chatbot

**Feature Branch**: `002-todo-ai-chatbot`
**Created**: 2025-12-19
**Protocol**: Model Context Protocol (MCP)

## Overview

This document defines the MCP tools exposed by the backend for the AI agent to manage user tasks. All tools operate on behalf of the authenticated user and follow Constitution Principle IX (Tool-Driven AI Behavior).

---

## Tool: add_task

Creates a new task for the user.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "maxLength": 2000,
      "description": "Optional task description"
    }
  },
  "required": ["user_id", "title"]
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" },
        "description": { "type": "string" },
        "is_completed": { "type": "boolean" },
        "created_at": { "type": "string", "format": "date-time" }
      }
    },
    "error": {
      "type": "string",
      "description": "Error message if success is false"
    }
  },
  "required": ["success"]
}
```

### Example
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Output:**
```json
{
  "success": true,
  "task": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "is_completed": false,
    "created_at": "2025-12-19T10:00:00Z"
  }
}
```

---

## Tool: list_tasks

Lists all tasks for the user, optionally filtered by completion status.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "completed": {
      "type": "boolean",
      "description": "Filter by completion status (optional)"
    }
  },
  "required": ["user_id"]
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string", "format": "uuid" },
          "title": { "type": "string" },
          "description": { "type": "string" },
          "is_completed": { "type": "boolean" },
          "created_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "count": {
      "type": "integer"
    },
    "error": {
      "type": "string"
    }
  },
  "required": ["success"]
}
```

### Example
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "completed": false
}
```

**Output:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "is_completed": false,
      "created_at": "2025-12-19T10:00:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "title": "Call mom",
      "description": null,
      "is_completed": false,
      "created_at": "2025-12-19T09:00:00Z"
    }
  ],
  "count": 2
}
```

---

## Tool: complete_task

Marks a task as completed.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "task_identifier": {
      "type": "string",
      "description": "Task ID (UUID) or title substring to match"
    }
  },
  "required": ["user_id", "task_identifier"]
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" },
        "is_completed": { "type": "boolean" }
      }
    },
    "error": {
      "type": "string"
    },
    "matches": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "title": { "type": "string" }
        }
      },
      "description": "If multiple tasks match, returns candidates for clarification"
    }
  },
  "required": ["success"]
}
```

### Example (Success)
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_identifier": "groceries"
}
```

**Output:**
```json
{
  "success": true,
  "task": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Buy groceries",
    "is_completed": true
  }
}
```

### Example (Ambiguous)
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_identifier": "report"
}
```

**Output:**
```json
{
  "success": false,
  "error": "Multiple tasks match 'report'. Please be more specific.",
  "matches": [
    { "id": "abc123", "title": "Sales report" },
    { "id": "def456", "title": "Expense report" }
  ]
}
```

---

## Tool: update_task

Updates a task's title or description.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "task_identifier": {
      "type": "string",
      "description": "Task ID (UUID) or title substring to match"
    },
    "title": {
      "type": "string",
      "maxLength": 200,
      "description": "New title (optional)"
    },
    "description": {
      "type": "string",
      "maxLength": 2000,
      "description": "New description (optional)"
    }
  },
  "required": ["user_id", "task_identifier"]
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" },
        "description": { "type": "string" }
      }
    },
    "error": {
      "type": "string"
    },
    "matches": {
      "type": "array",
      "items": {
        "type": "object"
      }
    }
  },
  "required": ["success"]
}
```

### Example
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_identifier": "groceries",
  "title": "Buy organic groceries"
}
```

**Output:**
```json
{
  "success": true,
  "task": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Buy organic groceries",
    "description": "Milk, eggs, bread"
  }
}
```

---

## Tool: delete_task

Permanently deletes a task.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authenticated user's ID"
    },
    "task_identifier": {
      "type": "string",
      "description": "Task ID (UUID) or title substring to match"
    }
  },
  "required": ["user_id", "task_identifier"]
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "deleted_task": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" }
      }
    },
    "error": {
      "type": "string"
    },
    "matches": {
      "type": "array",
      "items": {
        "type": "object"
      }
    }
  },
  "required": ["success"]
}
```

### Example
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_identifier": "old task"
}
```

**Output:**
```json
{
  "success": true,
  "deleted_task": {
    "id": "660e8400-e29b-41d4-a716-446655440003",
    "title": "old task"
  }
}
```

---

## Security Considerations

1. **User Isolation**: All tools receive `user_id` from the authenticated JWT, never from user input. The AI agent cannot access tasks belonging to other users.

2. **Input Validation**: All inputs are validated against schemas before execution. Invalid inputs return structured errors.

3. **Audit Trail**: Tool invocations and results are logged for debugging and security review.

4. **No Direct SQL**: Tools use SQLModel ORM; no raw SQL queries are permitted.

---

## Error Handling

All tools return structured error responses:

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

Common error conditions:
- Task not found: `"No task matching 'xyz' found"`
- Multiple matches: `"Multiple tasks match 'xyz'. Please be more specific."`
- Validation error: `"Title is required"`
- Database error: `"Unable to save task. Please try again."`
