# Implementation Plan: Todo In-Memory Python Console App

**Branch**: `001-todo-cli` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-cli/spec.md`

## Summary

Build a command-line todo application in Python 3.13+ that stores tasks in memory during runtime. The application provides a menu-driven interface for creating, viewing, updating, deleting, and managing task completion status. Implementation follows clean architecture principles with clear separation between models, services, and presentation layers.

**Core Value**: Enable users to track tasks during a terminal session with immediate feedback and simple CRUD operations.

**Technical Approach**: Single-project Python application using stdlib only (no external runtime dependencies), UV for package management, clean architecture with Models → Services → CLI layers, dictionary-based in-memory storage for O(1) task access.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (stdlib only for runtime); mypy, ruff, pytest for development
**Storage**: In-memory dictionary (no persistence)
**Testing**: pytest (if tests included in tasks phase)
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux terminals)
**Project Type**: Single project (CLI application)
**Performance Goals**: <100ms menu operations for up to 1000 tasks
**Constraints**: In-memory only (no file/DB I/O), single-user local execution, session-scoped data lifetime
**Scale/Scope**: Up to 1000 tasks, <50MB memory usage, deterministic behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Principle I: Spec-First Development
✅ **PASS** - Complete specification created with user stories, acceptance criteria, and requirements before planning began.

### Principle II: Clean Architecture
✅ **PASS** - Design follows Models → Services → CLI dependency flow:
- Models: Task entity (pure data)
- Services: TaskService (business logic, storage management)
- CLI: TodoCLI (presentation, user I/O)
- No circular dependencies

### Principle III: Simplicity and YAGNI
✅ **PASS** - Design choices favor simplicity:
- In-memory storage (no database)
- Sequential integer IDs (no UUID complexity)
- Stdlib only (no external runtime dependencies)
- Dataclass for Task (no ORM)
- Simple menu loop (no CLI framework)

### Principle IV: Python Best Practices
✅ **PASS** - Design incorporates:
- Full type hints for all function signatures (mypy validation)
- PEP 8 compliance (enforced by ruff)
- Docstrings for all classes and public methods
- Explicit exception handling with custom exception types
- Meaningful names following Python conventions

### Principle V: Test-Driven Development
⚠️ **CONDITIONAL** - Tests are OPTIONAL per tasks template:
- If tests included in tasks.md: TDD workflow mandatory (Red-Green-Refactor)
- If tests not included: Manual validation acceptable
- pytest configured as dev dependency for when needed

### Principle VI: Code Quality Gates
✅ **PASS** - Quality checks planned:
- Ruff for linting (PEP 8 compliance)
- Mypy for type checking (strict mode)
- Input validation for security (no injection risks)
- Clear error messages with custom exceptions
- No external attack surface (local only, no network/file I/O)

**Gate Status**: ALL PASSED - Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-cli/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (entities and services)
├── quickstart.md        # Phase 1 output (user guide)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   ├── task.py          # Task dataclass with business methods
│   └── exceptions.py    # TodoAppError, TaskNotFoundError, InvalidInputError
├── services/
│   ├── __init__.py
│   └── task_service.py  # TaskService class (CRUD operations, storage)
├── cli/
│   ├── __init__.py
│   └── todo_cli.py      # TodoCLI class (menu, I/O, formatting)
└── __main__.py          # Entry point (wire up service + CLI, run app)

tests/                   # If tests included in tasks phase
├── unit/
│   ├── test_task.py
│   └── test_task_service.py
└── integration/
    └── test_workflows.py

pyproject.toml           # UV project configuration
README.md                # Project overview and setup instructions
```

**Structure Decision**: Single project with clean architecture layering selected because:
- No web/mobile components (pure CLI)
- Clear separation supports constitution's clean architecture principle
- Manageable scope (4 user stories, ~500-800 LOC estimated)
- Follows Models → Services → Presentation dependency rule

## Phase 0: Research Summary

See [research.md](./research.md) for complete research findings. Key decisions:

### Technology Stack
- **Python 3.13+** with UV package manager (per spec TC-001, TC-002)
- **No runtime dependencies** (stdlib sufficient)
- **Dev dependencies**: mypy (type checking), ruff (linting/formatting), pytest (testing if needed)

### Storage Strategy
- **Dictionary-based in-memory storage**: `dict[int, Task]` for O(1) lookups
- **Sequential ID generation**: Simple counter starting at 1, no ID reuse
- **No persistence layer**: Intentionally session-scoped per spec FR-003

### Architecture Patterns
- **Clean Architecture**: Models → Services → CLI (no circular deps)
- **Dataclass for Task**: Simple, immutable ID, mutable title/description/completed
- **Service layer encapsulation**: All storage and business logic in TaskService
- **Custom exceptions**: TaskNotFoundError, InvalidInputError for clear error handling

### CLI Design
- **Simple menu loop**: Numbered options 1-7
- **Tabular task display**: ID | Title | Description | Status
- **Status indicators**: ✓ Complete / ✗ Incomplete
- **No CLI framework**: Direct stdin/stdout for simplicity

### Code Quality
- **Ruff**: Fast linting and formatting (PEP 8)
- **Mypy**: Static type checking (strict mode)
- **Type hints**: All function signatures
- **Docstrings**: All classes and public methods

## Phase 1: Design Summary

See [data-model.md](./data-model.md) for complete design documentation.

### Core Entity: Task

**Attributes**:
- `id: int` - Auto-generated, immutable, starts at 1
- `title: str` - Required, non-empty after strip
- `description: str` - Required, non-empty after strip
- `completed: bool` - Defaults to False

**Methods**:
- `mark_complete()` - Set completed to True
- `mark_incomplete()` - Set completed to False
- `update_title(new_title: str)` - Validate and update title
- `update_description(new_desc: str)` - Validate and update description

**Implementation**: Python dataclass with validation methods

### Service Layer: TaskService

**Storage**:
```python
_tasks: dict[int, Task]  # ID -> Task mapping
_next_id: int            # Sequential ID counter
```

**Operations**:
- `create_task(title, description) -> Task` - FR-002, FR-006, FR-007
- `get_task(task_id) -> Task` - Single task retrieval
- `get_all_tasks() -> list[Task]` - FR-005
- `update_task(task_id, title?, description?) -> Task` - FR-008
- `delete_task(task_id) -> None` - FR-011
- `mark_complete(task_id) -> Task` - FR-009
- `mark_incomplete(task_id) -> Task` - FR-009

**Validation**: All inputs validated, raises TaskNotFoundError or InvalidInputError

### Presentation Layer: TodoCLI

**Responsibilities**:
- Display menu (FR-001)
- Handle user input for all 7 operations
- Format task list display (FR-005)
- Display success/error feedback (FR-012)
- Graceful exit (FR-010)

**Key Methods**:
- `run()` - Main application loop
- `handle_add_task()` - Add workflow
- `handle_view_tasks()` - View workflow
- `handle_update_task()` - Update workflow
- `handle_delete_task()` - Delete workflow
- `handle_mark_complete()` - Mark complete workflow
- `handle_mark_incomplete()` - Mark incomplete workflow
- `format_task_list(tasks) -> str` - Tabular display

### Architecture Layers

```
CLI Layer (TodoCLI)
    ↓ depends on
Service Layer (TaskService)
    ↓ depends on
Model Layer (Task, Exceptions)
```

**Dependency Rule Verified**: ✅ Outer layers depend on inner, never reverse.

### Error Handling Strategy

**Exception Hierarchy**:
- `TodoAppError` (base)
  - `TaskNotFoundError` (invalid ID)
  - `InvalidInputError` (validation failures)

**Pattern**: Exceptions raised in service/model layers, caught in CLI layer, displayed as user-friendly messages.

## Performance Characteristics

Based on data-model.md analysis:

| Operation | Time Complexity | Meets <100ms Target |
|-----------|----------------|---------------------|
| Create task | O(1) | ✅ Yes |
| Get task by ID | O(1) | ✅ Yes |
| Get all tasks | O(n) | ✅ Yes (n≤1000) |
| Update task | O(1) | ✅ Yes |
| Delete task | O(1) | ✅ Yes |
| Mark complete/incomplete | O(1) | ✅ Yes |

**Memory**: Dictionary overhead + Task objects ≈ 50 bytes/task → ~50KB for 1000 tasks (well under 50MB limit)

## User Stories to Implementation Mapping

### User Story 1 (P1): Add and View Tasks
**Components**:
- `TaskService.create_task()` - Auto-generate ID, validate inputs, store task
- `TaskService.get_all_tasks()` - Retrieve all tasks ordered by ID
- `TodoCLI.handle_add_task()` - Collect title/description, call service
- `TodoCLI.handle_view_tasks()` - Get tasks, format and display table

**Fulfills**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-012

### User Story 2 (P2): Mark Tasks Complete/Incomplete
**Components**:
- `Task.mark_complete()` / `Task.mark_incomplete()` - State change methods
- `TaskService.mark_complete()` / `mark_incomplete()` - Lookup task, delegate to model
- `TodoCLI.handle_mark_complete()` / `handle_mark_incomplete()` - Get ID, call service

**Fulfills**: FR-009, FR-012

### User Story 3 (P3): Update Task Details
**Components**:
- `Task.update_title()` / `Task.update_description()` - Validation + update methods
- `TaskService.update_task()` - Lookup task, delegate to model
- `TodoCLI.handle_update_task()` - Get ID and new values, call service

**Fulfills**: FR-008, FR-012

### User Story 4 (P4): Delete Tasks
**Components**:
- `TaskService.delete_task()` - Remove from storage
- `TodoCLI.handle_delete_task()` - Get ID, call service, confirm deletion

**Fulfills**: FR-011, FR-012

### Cross-Cutting (All Stories)
**Components**:
- Exception hierarchy - Error handling (FR-004, SC-007)
- `TodoCLI.display_menu()` + `run()` - Menu loop (FR-001, FR-010)
- Input validation in all components (FR-004)

## Acceptance Criteria Verification

All 15 acceptance scenarios from spec.md map to implementation:

- ✅ Empty list → Add task → Auto ID + incomplete status (TaskService.create_task)
- ✅ View all tasks → Formatted table (TodoCLI.format_task_list)
- ✅ Status indicators distinct (✓/✗ in format_task_list)
- ✅ Mark complete → Status change (TaskService.mark_complete)
- ✅ Mark incomplete → Status change (TaskService.mark_incomplete)
- ✅ Invalid ID → Error message (TaskNotFoundError handling)
- ✅ Update title → Title changed (TaskService.update_task)
- ✅ Update description only → Description changed
- ✅ Update invalid ID → Error message
- ✅ Delete task → Removed from list (TaskService.delete_task)
- ✅ View after delete → Task not shown
- ✅ Delete invalid ID → Error message

## Edge Cases Handling

From spec.md edge cases:

1. **Invalid input (non-numeric ID, empty title/description)**
   - Solution: Input validation in CLI.get_int_input(), service validates strings
   - Raises InvalidInputError with clear message

2. **Very long titles/descriptions (100+ chars)**
   - Solution: No artificial limit imposed (simplicity), Python strings handle any length
   - Display may wrap in terminal (acceptable for CLI)

3. **Empty task list operations**
   - Solution: get_all_tasks() returns empty list (displays "No tasks" message)
   - Operations on IDs fail with TaskNotFoundError

4. **Task ID uniqueness with deletions**
   - Solution: Sequential counter never reused (spec assumption allows this)

5. **Duplicate titles**
   - Solution: Allowed (spec assumption), IDs distinguish tasks

## Success Criteria Verification

| Criterion | Implementation | Verified |
|-----------|---------------|----------|
| SC-001: Add+view in 3 actions | Menu → Add (enter title/desc) → View | ✅ |
| SC-002: Mark complete in 2 actions | Menu → Mark Complete (enter ID) → View | ✅ |
| SC-003: 1000 tasks <100ms | O(1) ops, O(n) display, Python dict performance | ✅ |
| SC-004: Feedback <1 second | Synchronous ops, immediate print statements | ✅ |
| SC-005: All workflows error-free | Exception handling in all CLI handlers | ✅ |
| SC-006: Clean start/exit | try-except in main, graceful exit option | ✅ |
| SC-007: Helpful error messages | Custom exceptions with user-friendly text | ✅ |

## Complexity Tracking

No constitution violations - complexity tracking table not needed.

All design decisions align with:
- ✅ Simplicity (no unnecessary abstractions)
- ✅ Clean architecture (proper layer separation)
- ✅ Python best practices (type hints, PEP 8, exceptions)
- ✅ Spec requirements (all FRs, NFRs, TCs covered)

## Post-Design Constitution Re-Check

### Principle I: Spec-First Development
✅ **PASS** - Specification complete before design, design derived from spec

### Principle II: Clean Architecture
✅ **PASS** - Models → Services → CLI verified in data-model.md, no violations

### Principle III: Simplicity and YAGNI
✅ **PASS** - Design choices reviewed:
- Dictionary storage: Simple, sufficient for requirements
- Sequential IDs: Simplest solution, spec allows
- No frameworks: Stdlib sufficient, no over-engineering
- No abstraction layers beyond necessary separation

### Principle IV: Python Best Practices
✅ **PASS** - Design incorporates all requirements:
- Type hints: All method signatures documented
- Docstrings: Planned for all classes/methods
- PEP 8: Enforced by ruff
- Exceptions: Custom hierarchy defined

### Principle V: Test-Driven Development
⚠️ **CONDITIONAL** - Awaiting tasks.md to determine if tests required

### Principle VI: Code Quality Gates
✅ **PASS** - Quality tools configured:
- Mypy (type checking)
- Ruff (linting/formatting)
- Input validation (security)
- Clear errors (UX)

**Final Gate Status**: ALL PASSED - Design approved, ready for tasks generation.

## ADR Recommendations

### Should We Document the Storage Decision?

**Three-Part Test**:
1. **Impact**: ✅ Affects all CRUD operations, central to architecture
2. **Alternatives**: ✅ Considered list-only, SQLite in-memory, dataclass with slots
3. **Scope**: ✅ Cross-cutting (every service operation depends on storage)

**Recommendation**: 📋 Architectural decision detected: In-Memory Storage Strategy (dict vs list vs SQLite)

Document reasoning and tradeoffs? Run `/sp.adr "In-Memory Storage Strategy for Task Management"`

### Should We Document the ID Generation Strategy?

**Three-Part Test**:
1. **Impact**: ⚠️ Moderate (affects task creation only)
2. **Alternatives**: ✅ Considered UUID, ID reuse with gap tracking
3. **Scope**: ⚠️ Localized to TaskService, not system-wide

**Recommendation**: No ADR needed - decision documented in research.md, not architecturally significant enough (doesn't affect multiple components).

## Next Steps

1. ✅ Phase 0 Research: Complete (research.md created)
2. ✅ Phase 1 Design: Complete (data-model.md, quickstart.md created)
3. ✅ Constitution Check: Passed (all principles verified)
4. ⏭️ **Phase 2**: Run `/sp.tasks` to generate implementation tasks from this plan
5. ⏭️ **Phase 3**: Run `/sp.implement` to execute tasks (TDD if tests included)

## Artifacts Summary

| Artifact | Status | Location |
|----------|--------|----------|
| Specification | ✅ Complete | specs/001-todo-cli/spec.md |
| Implementation Plan | ✅ Complete | specs/001-todo-cli/plan.md |
| Research | ✅ Complete | specs/001-todo-cli/research.md |
| Data Model | ✅ Complete | specs/001-todo-cli/data-model.md |
| Quickstart Guide | ✅ Complete | specs/001-todo-cli/quickstart.md |
| Tasks | ⏳ Pending | /sp.tasks command |
| Implementation | ⏳ Pending | /sp.implement command |

**Planning Phase Status**: COMPLETE - Ready for task generation.
