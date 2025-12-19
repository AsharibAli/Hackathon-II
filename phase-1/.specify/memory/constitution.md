<!--
Sync Impact Report:
Version Change: 1.0.0 (initial) → 1.0.0 (ratified)
Modified Principles: None (initial creation)
Added Sections: All core principles, quality standards, development workflow, governance
Removed Sections: None
Templates Status:
  ✅ plan-template.md - reviewed and compatible
  ✅ spec-template.md - reviewed and compatible
  ✅ tasks-template.md - reviewed and compatible
Follow-up TODOs: None
-->

# Todo CLI Application Constitution

## Core Principles

### I. Spec-First Development (NON-NEGOTIABLE)

No implementation before specification. Every feature MUST:
- Begin with a complete feature specification (`spec.md`)
- Include user stories with independent test scenarios
- Define clear acceptance criteria
- Be reviewed and approved before planning begins

**Rationale**: Spec-first development ensures alignment on requirements before investing in design and implementation, preventing wasted effort and rework.

### II. Clean Architecture

Code MUST follow clean architecture principles:
- Clear separation of concerns (models, services, presentation)
- Single Responsibility Principle for all classes and functions
- Dependencies flow inward (UI → Services → Models)
- No circular dependencies
- Business logic isolated from I/O and presentation

**Rationale**: Clean architecture enables testability, maintainability, and flexibility to change implementation details without affecting business logic.

### III. Simplicity and YAGNI

Implementation MUST favor simplicity:
- Build only what is specified - no extra features
- No premature abstraction or over-engineering
- In-memory storage is sufficient (no database complexity)
- Direct, straightforward code over clever solutions
- Delete unused code completely (no backwards-compatibility hacks)

**Rationale**: Simplicity reduces bugs, improves readability, and accelerates development. YAGNI (You Aren't Gonna Need It) prevents wasted effort on hypothetical requirements.

### IV. Python Best Practices

All Python code MUST:
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Include docstrings for classes and public methods
- Use meaningful, descriptive variable and function names
- Prefer composition over inheritance
- Handle errors explicitly with appropriate exception types

**Rationale**: Consistent code style and best practices improve code quality, readability, and maintainability across the codebase.

### V. Test-Driven Development (When Tests Required)

If tests are specified, TDD is mandatory:
- Write tests FIRST (Red phase)
- Ensure tests FAIL before implementation
- Implement to make tests pass (Green phase)
- Refactor while maintaining passing tests
- Tests must be independently executable

**Rationale**: TDD ensures code meets requirements, prevents regressions, and produces testable, modular code by design.

### VI. Code Quality Gates

All code MUST pass quality gates before completion:
- No linting errors (follow PEP 8)
- No type checking errors (mypy or similar)
- No security vulnerabilities (no injection risks, input validation)
- Clear error messages for user-facing failures
- Logging for debugging (where appropriate)

**Rationale**: Quality gates prevent technical debt, security issues, and maintainability problems from entering the codebase.

## Quality Standards

### Code Review Requirements

All changes MUST be:
- Self-contained and focused on a single feature or task
- Accompanied by clear commit messages
- Verified against specification requirements
- Free of unnecessary complexity
- Compliant with all core principles

### Security Requirements

Code MUST:
- Validate all user inputs
- Handle invalid data gracefully with clear error messages
- Prevent common vulnerabilities (injection, XSS if web-exposed later)
- Never expose sensitive information in logs or error messages
- Use secure defaults

### Performance Standards

For this in-memory CLI application:
- Commands MUST respond within 100ms for typical datasets (<1000 tasks)
- Memory usage MUST remain reasonable (<50MB for 1000 tasks)
- No performance optimization beyond these targets (simplicity first)

## Development Workflow

### Phase-Based Development

1. **Specification Phase** (`/sp.specify`):
   - Create feature specification with user stories
   - Define acceptance criteria
   - Identify entities and requirements
   - Get user approval

2. **Planning Phase** (`/sp.plan`):
   - Research technical approach
   - Design architecture and data models
   - Document design decisions
   - Create implementation plan
   - Suggest ADRs for significant decisions

3. **Task Generation** (`/sp.tasks`):
   - Break plan into concrete, testable tasks
   - Organize by user story for independent delivery
   - Include test tasks if required
   - Define dependencies and execution order

4. **Implementation Phase** (`/sp.implement`):
   - Execute tasks in dependency order
   - Create tests first (if required)
   - Implement to pass tests
   - Commit incrementally

5. **Documentation**:
   - Update README with usage instructions
   - Maintain architecture decision records (ADRs)
   - Keep prompt history records (PHRs) for all interactions

### Commit Strategy

Commits MUST:
- Be small and focused on single tasks
- Include descriptive messages following conventional commit format
- Reference task IDs where applicable
- Be made after each completed task or logical unit of work

### Architectural Decision Records (ADRs)

ADRs MUST be created when decisions meet all three criteria:
- **Impact**: Long-term consequences affecting architecture
- **Alternatives**: Multiple viable approaches were considered
- **Scope**: Cross-cutting concern influencing system design

Suggest ADRs proactively; require user consent before creation.

## Governance

### Constitution Authority

This constitution supersedes all other development practices. All code, plans, and specifications MUST comply with these principles.

### Amendment Process

Constitution amendments require:
1. Clear justification for the change
2. Impact assessment on existing artifacts
3. Version increment following semantic versioning:
   - MAJOR: Backward-incompatible principle changes
   - MINOR: New principles or significant expansions
   - PATCH: Clarifications, wording improvements
4. Update to dependent templates and documentation
5. Sync impact report documenting all changes

### Compliance Verification

All development phases MUST include constitution compliance checks:
- Specification: Verify alignment with Spec-First principle
- Planning: Verify Clean Architecture and Simplicity
- Tasks: Verify TDD approach if tests required
- Implementation: Verify all quality gates passed

### Complexity Justification

Any violation of simplicity or YAGNI principles MUST be justified in writing with:
- Specific requirement driving the complexity
- Explanation of why simpler alternatives are insufficient
- Plan to remove complexity when no longer needed

**Version**: 1.0.0 | **Ratified**: 2025-12-18 | **Last Amended**: 2025-12-18
