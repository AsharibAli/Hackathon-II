# Quickstart Guide: Todo In-Memory Python Console App

**Feature**: 001-todo-cli
**Version**: 1.0.0
**Date**: 2025-12-18

## Overview

This guide helps you get started with the Todo CLI application - a simple, in-memory task manager that runs in your terminal.

## Prerequisites

- **Python**: 3.13 or higher
- **Package Manager**: UV (install from [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv))
- **Operating System**: Windows, macOS, or Linux with terminal access

## Installation

### 1. Clone or Navigate to Project

```bash
cd path/to/Hackathon-II/phase-1
```

### 2. Initialize Project with UV

```bash
# Create virtual environment and install dependencies
uv sync

# Or if starting fresh:
uv init
```

### 3. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.13+

# Check UV installation
uv --version
```

## Running the Application

### Start the Todo App

```bash
# Option 1: Using UV
uv run python -m src

# Option 2: Activate venv first
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

python -m src
```

### You Should See

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

## Basic Usage

### Adding Your First Task

1. From the menu, enter `1` (Add Task)
2. Enter a title when prompted: `Buy groceries`
3. Enter a description: `Milk, eggs, bread`
4. You'll see: `✓ Task created with ID 1`

### Viewing All Tasks

1. From the menu, enter `2` (View All Tasks)
2. You'll see a formatted table:

```
ID | Title         | Description       | Status
---+---------------+-------------------+-----------
1  | Buy groceries | Milk, eggs, bread | ✗ Incomplete
```

### Marking a Task Complete

1. From the menu, enter `5` (Mark Task Complete)
2. Enter the task ID: `1`
3. You'll see: `✓ Task 1 marked as complete`

### Updating a Task

1. From the menu, enter `3` (Update Task)
2. Enter the task ID: `1`
3. Enter new title (or press Enter to skip): `Buy groceries and supplies`
4. Enter new description (or press Enter to skip): `Milk, eggs, bread, coffee`
5. You'll see: `✓ Task 1 updated successfully`

### Deleting a Task

1. From the menu, enter `4` (Delete Task)
2. Enter the task ID: `1`
3. You'll see: `✓ Task 1 deleted successfully`

### Exiting the Application

1. From the menu, enter `7` (Exit)
2. Application closes gracefully

**Note**: All data is lost when you exit (in-memory only).

## Common Workflows

### Daily Task Management

```
Start app
→ Add tasks for the day (option 1)
→ View all tasks (option 2)
→ Mark tasks as complete during the day (option 5)
→ View updated list (option 2)
→ Exit when done (option 7)
```

### Correcting Mistakes

```
Created task with typo
→ Update task (option 3)
→ Enter task ID
→ Enter corrected title/description
→ Verify with View All Tasks (option 2)
```

### Cleaning Up Completed Tasks

```
View all tasks (option 2)
→ Identify completed task IDs
→ Delete completed tasks (option 4)
→ View cleaned list (option 2)
```

## Features at a Glance

| Feature | Menu Option | Description |
|---------|-------------|-------------|
| **Add Task** | 1 | Create new task with title and description |
| **View All** | 2 | Display all tasks in a formatted table |
| **Update** | 3 | Modify title/description of existing task |
| **Delete** | 4 | Permanently remove a task |
| **Mark Complete** | 5 | Change task status to complete |
| **Mark Incomplete** | 6 | Change task status back to incomplete |
| **Exit** | 7 | Close application (data is lost) |

## Understanding Task Status

Tasks display status indicators in the task list:

- `✗ Incomplete` - Task not yet done (default for new tasks)
- `✓ Complete` - Task marked as finished

## Error Messages and Solutions

### "Task with ID X not found"

**Cause**: You entered an ID that doesn't exist.

**Solution**: View all tasks (option 2) to see valid IDs.

### "Title cannot be empty"

**Cause**: You entered only whitespace or empty string for title.

**Solution**: Enter at least one non-whitespace character.

### "Description cannot be empty"

**Cause**: You entered only whitespace or empty string for description.

**Solution**: Enter at least one non-whitespace character.

### "Invalid choice"

**Cause**: You entered something other than 1-7 for menu selection.

**Solution**: Enter a number between 1 and 7.

## Performance Notes

- The app is designed to handle up to 1000 tasks efficiently
- All operations complete in under 100ms
- Memory usage stays under 50MB even with many tasks
- No performance degradation with typical usage

## Data Persistence

**Important**: This application stores all data in memory only.

- ✅ Fast and simple
- ✅ No database setup required
- ❌ All data lost when app closes
- ❌ No data saved between sessions

This is intentional - perfect for temporary task tracking during a work session.

## Tips and Best Practices

### 1. Use Descriptive Titles

**Good**: "Buy groceries for weekend"
**Better**: "Buy groceries"

Keep titles concise - use description for details.

### 2. Add Tasks at Start of Session

Create all tasks you need to track at the beginning, then mark them complete as you go.

### 3. Review Before Exiting

View all tasks (option 2) before exiting to mentally note any incomplete tasks.

### 4. Use Update Instead of Delete+Add

If you made a mistake, use Update (option 3) to fix it rather than deleting and recreating.

### 5. IDs Are Sequential

Task IDs start at 1 and increment with each new task. Deleted IDs are not reused.

## Troubleshooting

### Application Won't Start

1. Check Python version: `python --version` (need 3.13+)
2. Check you're in correct directory
3. Try: `uv sync` to reinstall dependencies

### Menu Not Displaying Correctly

1. Verify terminal supports UTF-8 for status symbols
2. Try using a modern terminal (Windows Terminal, iTerm2, etc.)

### Can't Type Input

1. Make sure application is waiting for input (you see a prompt)
2. Try pressing Enter if cursor is stuck
3. Restart application if completely frozen

## Next Steps

- Try adding multiple tasks and practicing all operations
- Experiment with task updates and status toggling
- Use it for real task tracking during a work session!

## Support and Feedback

For issues or questions:
1. Check the error message - they're designed to be helpful
2. Review this guide for common solutions
3. Consult the specification in `specs/001-todo-cli/spec.md`

## Technical Details

For developers interested in the implementation:

- **Architecture**: Clean architecture (Models → Services → CLI)
- **Storage**: In-memory dictionary (O(1) lookups)
- **Error Handling**: Custom exceptions with user-friendly messages
- **Code Style**: PEP 8 compliant with full type hints
- **Testing**: Unit and integration tests (if implemented)

See `specs/001-todo-cli/data-model.md` for detailed architecture documentation.
