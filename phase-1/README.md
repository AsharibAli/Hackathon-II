# Todo CLI - In-Memory Python Console Application

A simple command-line todo application that stores tasks in memory during runtime. Built with Python 3.11+ using clean architecture principles.

## Features

- **Add Tasks**: Create new tasks with title and description
- **View Tasks**: Display all tasks in a formatted table with status indicators
- **Update Tasks**: Edit task titles and descriptions
- **Delete Tasks**: Remove tasks permanently
- **Mark Complete/Incomplete**: Toggle task completion status

## Prerequisites

- Python 3.11 or higher
- UV package manager ([installation guide](https://github.com/astral-sh/uv))

## Installation

1. Clone or navigate to the project directory:
```bash
cd path/to/Hackathon-II/phase-1
```

2. Install dependencies (if any dev tools needed):
```bash
uv sync --dev
```

## Usage

### Running the Application

```bash
# Using UV
uv run python -m src

# Or activate virtual environment first
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

python -m src
```

### Menu Options

When you run the application, you'll see:

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

### Example Workflow

1. **Add a task**: Select option 1, enter title and description
2. **View all tasks**: Select option 2 to see your task list
3. **Mark complete**: Select option 5, enter task ID
4. **Update task**: Select option 3, enter task ID and new details
5. **Delete task**: Select option 4, enter task ID
6. **Exit**: Select option 7

### Task Status Indicators

- `✗ Incomplete` - Task not yet finished (default)
- `✓ Complete` - Task marked as done

## Architecture

The application follows clean architecture with three layers:

```
src/
├── models/         # Domain entities (Task, exceptions)
├── services/       # Business logic (TaskService)
├── cli/            # User interface (TodoCLI)
└── __main__.py     # Application entry point
```

**Dependency Flow**: CLI → Services → Models (no circular dependencies)

## Important Notes

- **In-Memory Only**: All data is lost when the application exits
- **Session-Scoped**: Perfect for temporary task tracking during a work session
- **No Persistence**: No files or databases are used

## Development

### Code Quality Tools

```bash
# Run linter
uv run ruff check src/

# Run type checker
uv run mypy src/

# Format code
uv run ruff format src/
```

### Project Structure

- **src/models/**: Task dataclass and custom exceptions
- **src/services/**: TaskService with CRUD operations
- **src/cli/**: TodoCLI with menu and user interaction
- **specs/001-todo-cli/**: Design documents and specifications

## Technical Details

- **Language**: Python 3.11+
- **Package Manager**: UV
- **Storage**: In-memory dictionary (O(1) lookups)
- **Performance**: <100ms operations for up to 1000 tasks
- **Code Style**: PEP 8 compliant with full type hints

## Support

For questions or issues, refer to the specification in `specs/001-todo-cli/spec.md` or the quickstart guide in `specs/001-todo-cli/quickstart.md`.

## License

This project is part of a hackathon demonstration of spec-driven development.
