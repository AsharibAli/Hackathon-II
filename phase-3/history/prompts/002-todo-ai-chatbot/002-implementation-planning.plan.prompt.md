---
id: 002
title: Phase-3 AI chatbot implementation planning
stage: plan
date: 2025-12-19
surface: agent
model: claude-opus-4-5-20251101
feature: 002-todo-ai-chatbot
branch: 002-todo-ai-chatbot
user: unknown
command: /sp.plan
labels: ["plan", "phase-3", "ai-chatbot", "mcp", "architecture", "openai-agents"]
links:
  spec: specs/002-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-todo-ai-chatbot/plan.md
  - specs/002-todo-ai-chatbot/research.md
  - specs/002-todo-ai-chatbot/data-model.md
  - specs/002-todo-ai-chatbot/quickstart.md
  - specs/002-todo-ai-chatbot/contracts/chat-api.yaml
  - specs/002-todo-ai-chatbot/contracts/mcp-tools.md
tests:
  - None (planning document)
---

## Prompt

```text
Create an implementation plan derived from Phase-3 specifications.

====================================
PHASE 3.1: Spec Creation
====================================

- Create agent behavior spec
- Create MCP tools spec
- Create chat API spec

====================================
PHASE 3.2: Backend Augmentation
====================================

- Add OpenAI Agents SDK
- Add MCP Server using Official MCP SDK
- Implement MCP tools for task CRUD
- Add chat endpoint
- Implement JWT-secured access

====================================
PHASE 3.3: Conversation Persistence
====================================

- Store conversations in DB
- Store messages per conversation
- Rehydrate history per request

====================================
PHASE 3.4: Frontend Chat UI
====================================

- Replace task CRUD UI with ChatKit
- Configure domain allowlist
- Attach JWT to chat requests

====================================
PHASE 3.5: Validation
====================================

- Verify statelessness
- Test tool chaining
- Test conversation resumption
```

## Response snapshot

Created comprehensive implementation plan with 6 supporting artifacts:

**Phase 0: Research (research.md)**
- OpenAI Agents SDK selected for AI orchestration
- Official MCP SDK for tool protocol
- @assistant-ui/react for chat UI
- SQLModel + PostgreSQL for conversation persistence
- Single POST /api/chat endpoint design

**Phase 1: Data Model (data-model.md)**
- Conversation entity: id, user_id, created_at, updated_at
- Message entity: id, conversation_id, role, content, created_at
- User relationship extended with conversations
- Migration script template included

**Phase 1: Contracts**
- chat-api.yaml: OpenAPI 3.1 spec for chat endpoints
- mcp-tools.md: 5 MCP tools with input/output schemas

**Phase 1: Quickstart (quickstart.md)**
- Backend setup: dependencies, env vars, migration
- Frontend setup: @assistant-ui/react, ai SDK
- Verification steps and acceptance test scenarios
- Troubleshooting guide

**Implementation Plan (plan.md)**
- Constitution Check: All 10 principles PASS
- Project structure: Detailed file tree with new/modified files
- 5 implementation phases (3.1-3.5)
- Dependencies summary for backend and frontend
- Risk analysis and mitigations
- Definition of Done checklist

## Outcome

- ✅ Impact: Complete architectural plan for Phase-3 AI chatbot with all supporting documentation
- 🧪 Tests: None (planning documents)
- 📁 Files: Created 6 files (plan.md, research.md, data-model.md, quickstart.md, chat-api.yaml, mcp-tools.md)
- 🔁 Next prompts: Ready for `/sp.tasks` to generate task breakdown
- 🧠 Reflection: Plan maintains strict separation of concerns and stateless architecture per constitution; MCP tool approach provides auditable AI behavior

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check PASSED (10/10 principles)
- Prompt variant (if applicable): Standard /sp.plan with user-provided phase structure
- Next experiment (smallest change to try): Validate MCP SDK integration patterns during implementation; may need adjustment based on actual SDK API surface
