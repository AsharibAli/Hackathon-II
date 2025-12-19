# Data Model: Todo In-Memory Python Console App

**Feature**: 001-todo-cli
**Date**: 2025-12-18
**Phase**: 1 - Design

## Overview

This document defines the data entities, service interfaces, and domain logic for the Todo CLI application following clean architecture principles.

## Core Entities

### Task

Represents a single todo item as specified in the feature requirements.

**Attributes**:

| Attribute | Type | Description | Constraints | Default |
|-----------|------|-------------|-------------|---------|
| `id` | `int` | Unique identifier | Positive integer, immutable, auto-generated | Generated |
| `title` | `str` | Brief task name | Non-empty after strip, required | N/A |
| `description` | `str` | Detailed information | Non-empty after strip, required | N/A |
| `completed` | `bool` | Completion status | Boolean value | `False` |

**Invariants**:
- Once created, `id` cannot be changed
- `id` uniqueness guaranteed by TaskService
- `title` and `description` cannot be empty strings
- `completed` can only be `True` or `False`

**Python Implementation** (dataclass):

```python
from dataclasses import dataclass

@dataclass
class Task:
    """
    Represents a todo item.

    Attributes:
        id: Unique identifier (immutable)
        title: Brief task name
        description: Detailed task information
        completed: Completion status indicator
    """
    id: int
    title: str
    description: str
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete."""
        self.completed = False

    def update_title(self, new_title: str) -> None:
        """
        Update the task title.

        Args:
            new_title: New title (must be non-empty after strip)

        Raises:
            InvalidInputError: If new_title is empty
        """
        stripped = new_title.strip()
        if not stripped:
            raise InvalidInputError("Title cannot be empty")
        self.title = stripped

    def update_description(self, new_description: str) -> None:
        """
        Update the task description.

        Args:
            new_description: New description (must be non-empty after strip)

        Raises:
            InvalidInputError: If new_description is empty
        """
        stripped = new_description.strip()
        if not stripped:
            raise InvalidInputError("Description cannot be empty")
        self.description = stripped
```

**Design Rationale**:
- `dataclass` provides clean, concise syntax with automatic `__init__`, `__repr__`
- Methods encapsulate state changes (mark_complete, update_title, etc.)
- Validation in update methods ensures invariants
- Immutable ID enforced by convention (no setter method)

## Service Layer

### TaskService

Manages task storage and business operations. Implements all functional requirements related to task CRUD operations.

**Responsibilities**:
- Task creation with auto-generated IDs (FR-002, FR-006, FR-007)
- Task retrieval (single and all) (FR-005)
- Task updates (FR-008)
- Task deletion (FR-011)
- Completion status management (FR-009)
- Input validation (FR-004)
- In-memory storage management (FR-003)

**Interface**:

```python
class TaskService:
    """
    Service for managing tasks in memory.

    Handles all business logic for task operations including
    creation, retrieval, updates, deletion, and status management.
    """

    def __init__(self) -> None:
        """Initialize task service with empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def create_task(self, title: str, description: str) -> Task:
        """
        Create a new task with auto-generated ID.

        Args:
            title: Task title (will be stripped)
            description: Task description (will be stripped)

        Returns:
            Created task with unique ID and completed=False

        Raises:
            InvalidInputError: If title or description is empty after strip
        """
        ...

    def get_task(self, task_id: int) -> Task:
        """
        Retrieve a task by ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task with matching ID

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        ...

    def get_all_tasks(self) -> list[Task]:
        """
        Retrieve all tasks.

        Returns:
            List of all tasks ordered by ID (insertion order)
        """
        ...

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None
    ) -> Task:
        """
        Update task title and/or description.

        Args:
            task_id: ID of task to update
            title: New title (None means no change)
            description: New description (None means no change)

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
            InvalidInputError: If provided values are empty after strip
        """
        ...

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task permanently.

        Args:
            task_id: ID of task to delete

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        ...

    def mark_complete(self, task_id: int) -> Task:
        """
        Mark a task as completed.

        Args:
            task_id: ID of task to mark complete

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        ...

    def mark_incomplete(self, task_id: int) -> Task:
        """
        Mark a task as incomplete.

        Args:
            task_id: ID of task to mark incomplete

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        ...

    def _generate_id(self) -> int:
        """Generate next sequential ID."""
        ...
```

**Storage Design**:
```python
_tasks: dict[int, Task]  # ID -> Task mapping for O(1) lookups
_next_id: int            # Monotonically increasing ID counter
```

**Design Rationale**:
- Dictionary storage provides O(1) access by ID
- Sequential ID generation is simple and deterministic
- Service encapsulates all storage logic (models don't know about storage)
- Clear separation: models are data, service is logic
- All validation happens in service layer before touching models

## Exception Hierarchy

Custom exceptions for domain-specific error handling.

```python
class TodoAppError(Exception):
    """Base exception for all todo app errors."""
    pass

class TaskNotFoundError(TodoAppError):
    """Raised when attempting to access non-existent task."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task with ID {task_id} not found")
        self.task_id = task_id

class InvalidInputError(TodoAppError):
    """Raised when user provides invalid input."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
```

**Design Rationale**:
- Specific exceptions enable targeted error handling at CLI layer
- User-friendly error messages built into exceptions
- Inheritance from base exception allows catching all app errors

## Presentation Layer

### CLI Interface

Handles all user interaction including menu display, input parsing, and output formatting.

**Responsibilities**:
- Display menu and get user choice (FR-001)
- Collect input for operations (titles, descriptions, IDs)
- Format task lists for display (FR-005)
- Display success/error messages (FR-012)
- Graceful exit (FR-010)

**Key Components**:

```python
class TodoCLI:
    """
    Command-line interface for todo application.

    Handles all user I/O and delegates business logic to TaskService.
    """

    def __init__(self, service: TaskService) -> None:
        """Initialize CLI with task service."""
        self.service = service

    def run(self) -> None:
        """Main application loop."""
        ...

    def display_menu(self) -> None:
        """Display menu options."""
        ...

    def get_menu_choice(self) -> int:
        """Get and validate menu choice from user."""
        ...

    def handle_add_task(self) -> None:
        """Handle add task workflow."""
        ...

    def handle_view_tasks(self) -> None:
        """Handle view all tasks workflow."""
        ...

    def handle_update_task(self) -> None:
        """Handle update task workflow."""
        ...

    def handle_delete_task(self) -> None:
        """Handle delete task workflow."""
        ...

    def handle_mark_complete(self) -> None:
        """Handle mark complete workflow."""
        ...

    def handle_mark_incomplete(self) -> None:
        """Handle mark incomplete workflow."""
        ...

    def format_task_list(self, tasks: list[Task]) -> str:
        """Format tasks for display in tabular format."""
        ...

    def get_string_input(self, prompt: str) -> str:
        """Get non-empty string input from user."""
        ...

    def get_int_input(self, prompt: str) -> int:
        """Get integer input from user."""
        ...
```

**Display Format** (from research.md):

```
=== Todo App ===
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete
6. Mark Task Incomplete
7. Exit

Enter choice:
```

**Task List Format**:

```
ID | Title              | Description          | Status
---+--------------------+----------------------+-----------
1  | Buy groceries      | Milk, eggs, bread    | ✗ Incomplete
2  | Finish project     | Complete todo app    | ✓ Complete
```

**Design Rationale**:
- CLI class depends on TaskService (dependency injection)
- Each menu option has dedicated handler method
- All user input goes through validation helpers
- Presentation logic isolated from business logic
- Try-except in handlers to catch service exceptions and display user-friendly messages

## Data Flow

### Create Task Flow

```
User Input → CLI.handle_add_task()
          → CLI.get_string_input("Title: ")
          → CLI.get_string_input("Description: ")
          → TaskService.create_task(title, desc)
          → Task.__init__(id, title, desc, False)
          → Store in service._tasks
          → Return Task
          → CLI displays success message
```

### View Tasks Flow

```
User Input → CLI.handle_view_tasks()
          → TaskService.get_all_tasks()
          → Return list[Task] from _tasks.values()
          → CLI.format_task_list(tasks)
          → Display formatted table
```

### Update Task Flow

```
User Input → CLI.handle_update_task()
          → CLI.get_int_input("Task ID: ")
          → CLI.get_string_input("New title: ") [optional]
          → CLI.get_string_input("New description: ") [optional]
          → TaskService.update_task(id, title, desc)
          → Task.update_title() and/or Task.update_description()
          → Return updated Task
          → CLI displays success message
```

### Error Handling Flow

```
User Input → CLI handler
          → TaskService operation
          → Validation fails or task not found
          → Raise TaskNotFoundError or InvalidInputError
          → CLI catches exception
          → Display user-friendly error message
          → Return to menu (don't crash)
```

## Architecture Layers

Following Constitution Principle II (Clean Architecture):

```
┌─────────────────────────────────────┐
│   CLI Layer (Presentation)          │  ← User interaction
│   - TodoCLI class                    │
│   - Input/output handling            │
└─────────────────────────────────────┘
            ↓ depends on
┌─────────────────────────────────────┐
│   Service Layer (Business Logic)    │  ← Domain operations
│   - TaskService class                │
│   - Validation, ID generation        │
└─────────────────────────────────────┘
            ↓ depends on
┌─────────────────────────────────────┐
│   Model Layer (Domain Entities)     │  ← Pure data
│   - Task dataclass                   │
│   - Domain exceptions                │
└─────────────────────────────────────┘
```

**Dependency Rule**: Outer layers depend on inner layers, never the reverse.
- CLI knows about TaskService and Task
- TaskService knows about Task
- Task knows nothing about TaskService or CLI

## File Organization

Based on research.md project structure:

```
src/
├── models/
│   ├── __init__.py
│   ├── task.py          # Task dataclass
│   └── exceptions.py    # TodoAppError, TaskNotFoundError, InvalidInputError
├── services/
│   ├── __init__.py
│   └── task_service.py  # TaskService class
├── cli/
│   ├── __init__.py
│   └── todo_cli.py      # TodoCLI class
└── __main__.py          # Entry point: creates service, creates CLI, runs CLI
```

## Validation Rules Summary

| Input | Validation | Error Type |
|-------|------------|------------|
| Task ID | Must be positive int, must exist in storage | TaskNotFoundError |
| Title | Must be non-empty after strip() | InvalidInputError |
| Description | Must be non-empty after strip() | InvalidInputError |
| Menu choice | Must be 1-7 | InvalidInputError |
| Numeric input | Must parse as int | InvalidInputError |

## State Transitions

### Task Completion State Machine

```
      ┌─────────────┐
      │  Incomplete │ (default on creation)
      └──────┬──────┘
             │
    mark_complete()
             │
             ↓
      ┌──────────┐
      │ Complete │
      └────┬─────┘
           │
  mark_incomplete()
           │
           ↓
      ┌─────────────┐
      │  Incomplete │
      └─────────────┘
```

Simple boolean toggle - no complex state management needed.

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Create task | O(1) | O(1) |
| Get task by ID | O(1) | O(1) |
| Get all tasks | O(n) | O(n) |
| Update task | O(1) | O(1) |
| Delete task | O(1) | O(1) |
| Mark complete/incomplete | O(1) | O(1) |

Where n = number of tasks (max 1000 per performance target).

All operations meet the <100ms requirement for up to 1000 tasks.

## Next Steps

1. Create `quickstart.md` with user guide
2. Update `plan.md` with complete technical context
3. Await `/sp.tasks` command to generate implementation tasks
