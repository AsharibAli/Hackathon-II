---
id: 002
title: Phase-3 AI CUI constitution update
stage: constitution
date: 2025-12-19
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: unknown
command: /sp.constitution
labels: ["constitution", "amendment", "phase-3", "ai-agents", "mcp", "cui"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (documentation only)
---

## Prompt

```text
You are Claude Code acting as a senior AI systems engineer executing Phase-3 of a Spec-Driven Development workflow using Spec-Kit Plus.

====================================
PHASE-3 OBJECTIVE
====================================

Extend the existing Phase-2 Todo Full-Stack Web Application into an AI-powered Conversational User Interface (CUI).

This phase introduces:
- Natural language task management
- AI agents powered by OpenAI Agents SDK
- An MCP (Model Context Protocol) server exposing task operations as tools

The existing Phase-2 frontend, backend, authentication, and database code is preserved and reused.

====================================
CORE PRINCIPLES
====================================

- Spec-first development is mandatory
- No manual coding; Claude Code performs all changes
- Phase-2 functionality must remain intact
- Conversational interface replaces GUI task interactions
- All AI behavior must be tool-driven via MCP

====================================
ARCHITECTURAL CONSTRAINTS
====================================

Frontend:
- Next.js (App Router)
- Tailwind CSS
- shadcn/ui
- OpenAI ChatKit UI

Backend:
- FastAPI
- SQLModel
- Neon PostgreSQL
- OpenAI Agents SDK
- Official MCP SDK

====================================
KEY DESIGN RULE
====================================

The server must be stateless.
All conversation and task state must be persisted in the database.
```

## Response snapshot

Successfully amended the project constitution from v1.0.0 to v1.1.0 (MINOR version bump).

**New Principles Added (Phase-3):**
- **VIII. Stateless Server Architecture**: No in-memory state; all session and AI agent state persisted in PostgreSQL; enables horizontal scaling
- **IX. Tool-Driven AI Behavior (MCP)**: AI agents MUST use MCP tools for all operations; prevents prompt injection; provides auditable AI actions
- **X. Conversation Persistence**: All messages stored in database; multi-turn context preserved; tool calls logged for debugging

**Updated Architectural Constraints:**
- Added OpenAI ChatKit UI to frontend stack
- Added OpenAI Agents SDK to backend stack
- Added Official MCP SDK to backend stack
- Added 3 new constraint validations for AI/MCP components

**Preserved Principles (I-VII):**
All original Phase-2 principles retained without modification, ensuring backward compatibility with existing implementation.

## Outcome

- ✅ Impact: Constitution extended with 3 new AI/CUI-specific principles, enabling Phase-3 development while preserving all Phase-2 governance
- 🧪 Tests: None (governance document)
- 📁 Files: Updated .specify/memory/constitution.md (v1.0.0 → v1.1.0, 256 lines)
- 🔁 Next prompts: Ready for `/sp.specify` to create Phase-3 CUI feature specification
- 🧠 Reflection: MINOR version bump appropriate as new principles ADD to existing governance without changing existing principle semantics; stateless architecture principle critical for production scalability

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable (documentation amendment)
- Prompt variant (if applicable): Standard constitution amendment via /sp.constitution with Phase-3 scope
- Next experiment (smallest change to try): Validate new MCP/AI principles against upcoming Phase-3 spec to ensure sufficient coverage for AI agent safety and controllability
