# Research: Todo In-Memory Python Console App

**Feature**: 001-todo-cli
**Date**: 2025-12-18
**Phase**: 0 - Research & Technology Selection

## Overview

This document captures research findings and technical decisions for implementing the Todo CLI application based on the feature specification.

## Technology Stack Decisions

### 1. Python Version and Package Management

**Decision**: Python 3.13+ with UV package manager

**Rationale**:
- Python 3.13 provides latest language features and performance improvements
- UV is a fast, modern Python package manager (specified in technical constraints TC-002)
- UV offers excellent dependency resolution and project scaffolding
- No external dependencies required for core functionality (in-memory only)

**Alternatives Considered**:
- Poetry: More established but slower than UV
- pip + venv: Standard but lacks modern project management features

**Implementation Notes**:
- Use `uv init` to create project structure
- Use `uv add` for any development dependencies (linting, type checking)
- No runtime dependencies needed (stdlib sufficient for CLI and data structures)

### 2. Project Structure Pattern

**Decision**: Single project with clean architecture layering

**Rationale**:
- Spec requires clean separation of concerns (NFR-001)
- Constitution Principle II mandates Models → Services → Presentation flow
- Single project appropriate for focused CLI application
- No web/mobile components detected

**Structure**:
```
src/
├── models/          # Data models (Task entity)
├── services/        # Business logic (TaskService)
├── cli/            # Presentation layer (menu, I/O)
└── __main__.py     # Application entry point

tests/              # Tests (if required in tasks phase)
├── unit/           # Unit tests for models and services
└── integration/    # Integration tests for full workflows
```

**Alternatives Considered**:
- Flat structure: Rejected - violates clean architecture principle
- Separate packages: Over-engineering for this scope

### 3. Data Storage Strategy

**Decision**: Python list with dictionary-based task lookup

**Rationale**:
- Spec requires in-memory only (FR-003, TC-003)
- List provides ordered storage (maintains insertion order)
- Dict lookup by ID provides O(1) access for updates/deletes
- No persistence layer needed (Constitution Principle III: Simplicity)

**Implementation Approach**:
```python
# In TaskService
self._tasks: dict[int, Task] = {}  # ID -> Task mapping
self._next_id: int = 1  # Sequential ID generator
```

**Alternatives Considered**:
- List only: O(n) lookups inefficient for 1000 tasks
- SQLite in-memory: Over-engineering, violates simplicity
- dataclass with __slots__: Premature optimization

### 4. ID Generation Strategy

**Decision**: Simple sequential integer counter

**Rationale**:
- Spec requires auto-generated unique IDs starting from 1 (FR-002)
- Assumption allows simple incrementing integers (spec assumptions section)
- No ID reuse after deletion acceptable (FR-011)
- Deterministic and straightforward

**Implementation**:
```python
def _generate_id(self) -> int:
    current_id = self._next_id
    self._next_id += 1
    return current_id
```

**Alternatives Considered**:
- UUID: Overkill for in-memory, single-user app
- ID reuse with gap tracking: Violates simplicity, spec doesn't require it

### 5. Input Validation Strategy

**Decision**: Explicit validation with custom exception types

**Rationale**:
- Spec requires input validation with clear error messages (FR-004, SC-007)
- Constitution Principle IV: Explicit error handling
- Constitution Principle VI: Clear error messages required

**Validation Rules**:
- Task ID: Must be positive integer, must exist in storage
- Title: Must be non-empty string (after strip)
- Description: Must be non-empty string (after strip)
- Menu choice: Must be valid menu option

**Exception Hierarchy**:
```python
class TodoAppError(Exception):
    """Base exception for todo app errors"""

class TaskNotFoundError(TodoAppError):
    """Raised when task ID doesn't exist"""

class InvalidInputError(TodoAppError):
    """Raised for invalid user inputs"""
```

**Alternatives Considered**:
- Generic exceptions: Rejected - doesn't provide clear error context
- Error codes: Less Pythonic than exceptions

### 6. Type Hints and Type Checking

**Decision**: Full type hints with mypy for static analysis

**Rationale**:
- Constitution Principle IV: Type hints mandatory for all function signatures
- Constitution Principle VI: No type checking errors allowed
- Python 3.13 supports modern type syntax (PEP 604 unions, etc.)

**Implementation**:
- Type hint all function parameters and return values
- Use `from typing import Protocol` for interface definitions if needed
- Configure mypy with strict settings
- Use `uv add --dev mypy` for type checking

**Alternatives Considered**:
- Pyright: Good but mypy is industry standard for Python
- No type checking: Violates constitution

### 7. Code Quality Tools

**Decision**: Ruff for linting and formatting

**Rationale**:
- Constitution Principle IV: PEP 8 compliance mandatory
- Constitution Principle VI: No linting errors allowed
- Ruff is extremely fast and combines linter + formatter
- UV ecosystem compatibility

**Configuration**:
- Ruff for linting (replaces flake8, pylint)
- Ruff format for code formatting (replaces black)
- Line length: 100 characters (modern standard)
- Enable PEP 8 rules, type checking support, docstring rules

**Alternatives Considered**:
- Black + flake8: Slower, more tools to maintain
- Pylint: Good but slower than Ruff

### 8. CLI Implementation Pattern

**Decision**: Simple menu loop with numbered options

**Rationale**:
- Spec requires menu-driven interface (FR-001)
- Users understand basic CLI conventions (spec assumptions)
- Simple is better than complex (Constitution Principle III)
- No CLI framework needed (argparse, click) - just stdin/stdout

**Menu Structure**:
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

**User Flow**:
- Display menu
- Get numeric choice
- Execute action with sub-prompts for inputs
- Display result/error message
- Loop until exit

**Alternatives Considered**:
- Click framework: Over-engineering for simple menu
- Argparse with subcommands: Not menu-driven as spec requires
- Rich/Textual TUI: Violates simplicity, spec says "CLI"

### 9. Task Display Format

**Decision**: Tabular format with status indicators

**Rationale**:
- Spec requires readable format with ID, title, description, status (FR-005)
- Status must be visually distinct (User Story 1, acceptance scenario 3)
- Plain text output (no external dependencies)

**Format Example**:
```
ID | Title              | Description          | Status
---+--------------------+----------------------+-----------
1  | Buy groceries      | Milk, eggs, bread    | ✗ Incomplete
2  | Finish project     | Complete todo app    | ✓ Complete
```

**Alternatives Considered**:
- JSON output: Not readable for humans
- Rich tables: External dependency, violates simplicity
- Simple list: Less structured, harder to scan

### 10. Error Handling and User Feedback

**Decision**: Try-except at CLI layer with user-friendly messages

**Rationale**:
- Spec requires clear error messages (FR-004, FR-012, SC-007)
- Exceptions should be caught at presentation layer
- User sees friendly message, not stack trace
- All operations must give feedback within 1 second (SC-004)

**Pattern**:
```python
try:
    service.some_operation()
    print("✓ Success message")
except TaskNotFoundError:
    print("✗ Error: Task not found")
except InvalidInputError as e:
    print(f"✗ Error: {e}")
```

**Alternatives Considered**:
- Return codes: Less Pythonic than exceptions
- Logging errors to file: Spec forbids file I/O

## Performance Considerations

### Target Performance (from spec SC-003, NFR-004)
- Support up to 1000 tasks
- Menu operations complete within 100ms
- Memory usage under 50MB (constitution performance standards)

### Implementation Implications
- Dictionary lookup ensures O(1) task access
- No optimization needed for 1000 tasks - Python's built-ins are sufficient
- Avoid premature optimization (Constitution Principle III)

## Testing Approach (if tests required)

### Test Framework Decision

**Decision**: pytest if tests are included in tasks phase

**Rationale**:
- Industry standard for Python testing
- Clean syntax, excellent assertion messages
- Easy to use with type hints and fixtures
- Constitution Principle V: TDD when tests required

**Test Structure** (if applicable):
```
tests/
├── unit/
│   ├── test_task_model.py
│   └── test_task_service.py
└── integration/
    └── test_workflows.py
```

**Note**: Tests are OPTIONAL per tasks template. Will only implement if specified in tasks.md.

## Security Considerations

### Input Validation (Constitution Security Requirements)
- Validate all user inputs before processing
- Sanitize strings to prevent injection (though CLI context limits risk)
- No sensitive data handling required (single-user, local app)
- Clear error messages without exposing internals

### No External Attack Surface
- No network I/O
- No file I/O
- No database connections
- No user authentication
- Single-user, local execution only

## Development Dependencies

```toml
[dev-dependencies]
mypy = "latest"      # Type checking
ruff = "latest"      # Linting and formatting
pytest = "latest"    # Testing (if tests required)
```

**No runtime dependencies** - stdlib only for production code.

## Open Questions / Clarifications

None - all technical decisions align with specification and constitution requirements.

## Next Steps

Phase 1 artifacts to create:
1. `data-model.md` - Detailed Task entity and service interface design
2. `quickstart.md` - User guide for running and using the application
3. Update `plan.md` with final technical context and project structure

Phase 2 (separate command):
1. `/sp.tasks` to generate implementation tasks based on this plan
