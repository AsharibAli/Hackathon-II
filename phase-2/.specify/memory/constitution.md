<!--
Sync Impact Report:
Version Change: 1.0.0 → 1.0.0 (Initial constitution ratification)
Modified Principles: None (initial creation)
Added Sections:
  - Core Principles (7 principles)
  - Architectural Constraints
  - Development Workflow
  - Governance
Removed Sections: None (initial creation)
Templates Status:
  - ✅ .specify/templates/plan-template.md (Constitution Check section exists)
  - ✅ .specify/templates/spec-template.md (Requirements alignment verified)
  - ✅ .specify/templates/tasks-template.md (Task categorization aligned)
  - ⚠️ README.md (Does not exist yet - will need creation after initial implementation)
Follow-up TODOs: Create README.md once initial project structure is established
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-First Development (NON-NEGOTIABLE)

No code implementation shall begin before a complete specification is written, reviewed, and approved. Every feature MUST follow this workflow:

1. Specification (`/sp.specify`) → User approval
2. Planning (`/sp.plan`) → User approval
3. Task generation (`/sp.tasks`) → User approval
4. Implementation (`/sp.implement`) → Only after all approvals

**Rationale**: Prevents rework, ensures alignment with requirements, maintains project documentation quality, and enables proper architectural review before committing to an implementation path.

### II. Single Code Authority

Claude Code is the ONLY entity permitted to write code. Human developers provide specifications, review outputs, and approve decisions, but MUST NOT directly write implementation code.

**Rationale**: Ensures consistent code quality, enforces spec-driven workflow, maintains architectural coherence, and prevents drift from specifications.

### III. Separation of Concerns

Frontend and backend responsibilities MUST remain strictly separated:

- **Frontend**: UI components, client-side state, user interactions, API client calls
- **Backend**: Business logic, database operations, authentication, API endpoints
- **No mixing**: Backend logic MUST NOT appear in frontend code; frontend concerns MUST NOT leak into backend

**Rationale**: Enables independent development, testing, and deployment of each layer; improves maintainability and supports team specialization.

### IV. Authentication & Authorization Enforcement

Every API request MUST enforce authentication and authorization:

- All endpoints (except public routes like `/auth/login`, `/auth/register`) MUST verify JWT tokens
- User identity MUST be extracted from validated tokens
- Data access MUST be scoped to the authenticated user
- Multi-user isolation MUST be guaranteed at the database query level

**Rationale**: Ensures secure multi-user operation, prevents unauthorized data access, maintains data privacy, and meets security compliance requirements.

### V. Test-First When Specified

When tests are explicitly requested in specifications:

- Tests MUST be written BEFORE implementation
- Tests MUST FAIL initially (Red phase)
- Implementation makes tests pass (Green phase)
- Code is then refactored while keeping tests passing (Refactor phase)
- Contract tests verify API boundaries
- Integration tests verify user journeys

**Rationale**: Validates requirements understanding, prevents regression, ensures testable architecture, and provides executable specifications.

### VI. Database Persistence First

All application data MUST be persisted in PostgreSQL:

- No in-memory-only data structures for user data
- SQLModel ORM MUST be used for all database operations
- Migrations MUST be version-controlled and reversible
- Schema changes MUST be applied via migrations, never manual SQL

**Rationale**: Ensures data durability, enables rollback capabilities, maintains schema consistency across environments, and supports multiple concurrent users.

### VII. Observability & Debuggability

All code MUST support operational visibility:

- Structured logging at appropriate levels (INFO, WARNING, ERROR)
- Request correlation IDs for distributed tracing
- Error responses MUST include actionable context (without leaking sensitive data)
- Performance-critical operations MUST be instrumented

**Rationale**: Enables rapid debugging, supports production monitoring, facilitates performance optimization, and reduces mean time to resolution for incidents.

## Architectural Constraints

### Technology Stack (MANDATORY)

The following technologies are NON-NEGOTIABLE and MUST be used:

**Monorepo Structure**:
- Spec-Kit Plus conventions MUST be followed
- `backend/` and `frontend/` as top-level directories
- Shared specifications under `specs/`
- Shared governance under `.specify/memory/`

**Frontend Stack**:
- Framework: Next.js with App Router (latest stable)
- Language: TypeScript (strict mode enabled)
- Styling: Tailwind CSS
- UI Components: shadcn/ui
- Package Manager: pnpm (ONLY - no npm or yarn)

**Backend Stack**:
- Framework: FastAPI (Python 3.11+)
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT
- Package Manager: uv (ONLY - no pip or poetry)

**Rationale**: Standardizes tooling, ensures team familiarity, leverages modern best practices, and minimizes decision paralysis during implementation.

### Constraint Validations

All implementation plans MUST validate against these constraints:

- ✅ TypeScript strict mode enabled in `tsconfig.json`
- ✅ FastAPI app properly configured with CORS, middleware, exception handlers
- ✅ SQLModel models use proper type annotations and relationships
- ✅ Better Auth integrated with JWT secret from environment variables
- ✅ Neon database connection string stored securely in `.env` (never committed)

## Development Workflow

### Workflow Stages

1. **Specification** (`/sp.specify`): Capture user requirements, acceptance criteria, success metrics
2. **Planning** (`/sp.plan`): Design architecture, define structure, identify dependencies
3. **Task Generation** (`/sp.tasks`): Break down implementation into ordered, testable tasks
4. **Implementation** (`/sp.implement`): Execute tasks with progress tracking and validation
5. **ADR Documentation** (`/sp.adr`): Capture significant architectural decisions when detected

### Quality Gates

Each stage MUST pass these gates before proceeding:

**Specification Gate**:
- All user stories have acceptance criteria
- Edge cases are documented
- Success criteria are measurable
- No unresolved `[NEEDS CLARIFICATION]` markers

**Planning Gate**:
- Constitution compliance verified
- Technology stack matches constraints
- Project structure follows monorepo conventions
- Dependencies identified and justified

**Task Gate**:
- Tasks reference specific file paths
- Dependencies between tasks clearly marked
- Parallel execution opportunities identified ([P] markers)
- Each task is independently testable

**Implementation Gate**:
- All tasks completed and verified
- Tests passing (if specified)
- No hardcoded secrets or credentials
- Code follows language-specific conventions

### Human-as-Tool Strategy

Claude Code MUST invoke the user for:

1. **Ambiguous Requirements**: Ask 2-3 targeted clarifying questions before proceeding
2. **Architectural Uncertainty**: Present options with tradeoffs, get user preference
3. **Unforeseen Dependencies**: Surface them and ask for prioritization
4. **Completion Checkpoints**: Summarize what was done, confirm next steps

**Rationale**: Treats human judgment as a specialized resource for decisions requiring context, preference, or domain expertise that AI cannot infer.

## Governance

### Amendment Process

This constitution may be amended through:

1. Documented proposal with rationale
2. User approval
3. Version increment following semantic versioning:
   - **MAJOR**: Backward-incompatible principle removals or redefinitions
   - **MINOR**: New principles or materially expanded sections
   - **PATCH**: Clarifications, wording improvements, non-semantic refinements
4. Update to all dependent templates and guidance files
5. Commit with message: `docs: amend constitution to vX.Y.Z`

### Compliance

All work MUST comply with this constitution:

- PRs and reviews MUST verify compliance
- Violations MUST be justified in plan.md "Complexity Tracking" section
- Templates MUST reference constitution principles where applicable
- ADRs MUST reference relevant constitutional principles when making decisions

### Runtime Guidance

For agent-specific runtime development guidance, refer to `CLAUDE.md` (primary) and this constitution (governance).

**Version**: 1.0.0 | **Ratified**: 2025-12-18 | **Last Amended**: 2025-12-18
