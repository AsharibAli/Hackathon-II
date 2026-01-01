<p align="center">
  <img src="frontend/public/favicon.svg" height="80" alt="TaskAI Logo" />
</p>

<h1 align="center">TaskAI</h1>

<p align="center">
  <strong>Advanced AI-Powered Task Management with Dual Interface</strong>
</p>

<p align="center">
  A modern, intelligent task management application featuring both <strong>Conversational (CUI)</strong> and <strong>Graphical (GUI)</strong> interfaces. Built with cloud-native microservices architecture using FastAPI, Next.js, and MCP (Model Context Protocol) for seamless AI integration.
</p>

<p align="center">
  <a href="#features"><strong>Features</strong></a> ·
  <a href="#tech-stack"><strong>Tech Stack</strong></a> ·
  <a href="#getting-started"><strong>Getting Started</strong></a> ·
  <a href="#deployment"><strong>Deployment</strong></a> ·
  <a href="#api-reference"><strong>API Reference</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16+-black?style=flat-square&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.125+-009688?style=flat-square&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/OpenAI-MCP-412991?style=flat-square&logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=flat-square&logo=kubernetes&logoColor=white" alt="Kubernetes" />
  <img src="https://img.shields.io/badge/Dapr-Microservices-0D2192?style=flat-square&logo=dapr&logoColor=white" alt="Dapr" />
</p>

---

## Overview

TaskAI revolutionizes task management by offering two seamless ways to interact with your tasks:

- **Chat Mode (CUI)**: Natural language task management powered by OpenAI and MCP tools
- **Tasks Mode (GUI)**: Traditional visual interface with advanced filtering and organization

Both interfaces share the same backend, ensuring real-time synchronization across modes.

### Key Highlights

| Feature | Description |
|---------|-------------|
| **Dual Interface** | Switch between AI chat and traditional GUI anytime |
| **AI-Powered** | Natural language understanding via OpenAI with MCP tool integration |
| **Multi-User** | Secure user isolation with JWT authentication |
| **Real-Time Sync** | Tasks created in one mode appear instantly in the other |
| **Cloud-Native** | Kubernetes-ready with Helm charts and Dapr microservices |
| **Event-Driven** | Pub/sub architecture for notifications and recurring tasks |

---

## Features

### Chat Mode (Conversational UI)

Interact with your tasks using natural language:

```
You: "Add a high priority task to review the quarterly report by Friday"
AI: "Done! I've created 'review the quarterly report' with high priority, due Friday."

You: "Show me my overdue tasks"
AI: "You have 2 overdue tasks:
     1. Submit expense report (high priority, due Dec 20)
     2. Reply to client email (medium priority, due Dec 22)"

You: "Mark the expense report as done"
AI: "I've marked 'Submit expense report' as completed."
```

**Available AI Tools (MCP Protocol):**

| Tool | Description |
|------|-------------|
| `create_task` | Create new tasks with title and description |
| `list_tasks` | View all tasks with optional filtering |
| `complete_task` | Mark tasks as completed |
| `delete_task` | Remove tasks permanently |
| `update_task` | Modify task details |
| `set_priority` | Set priority (high/medium/low) |
| `add_tag` / `remove_tag` | Manage task tags |
| `set_due_date` | Set or update due dates |
| `set_reminder` | Schedule task reminders |
| `set_recurrence` | Configure recurring patterns |
| `search_tasks` | Full-text search across tasks |
| `filter_by_priority` | Filter by priority level |
| `filter_by_tag` | Filter by tag name |
| `show_overdue` | List all overdue tasks |
| `combined_filter` | Multi-criteria filtering |
| `sort_tasks` | Sort by various fields |

### Tasks Mode (Graphical UI)

Traditional visual interface with powerful features:

- **Task Creation**: Form with title, description, priority, tags, due date
- **Priority System**: High (red), Medium (yellow), Low (green) color coding
- **Tag Management**: Create, assign, and filter by custom tags
- **Due Dates**: Date picker with overdue highlighting
- **Reminders**: Schedule notifications for important tasks
- **Recurrence**: Daily, weekly, monthly recurring tasks
- **Advanced Search**: Full-text search with result highlighting
- **Smart Filtering**: Filter by priority, status, tags, overdue
- **Flexible Sorting**: Sort by due date, priority, created date

### Authentication & Security

- **JWT Authentication**: Secure token-based auth with 24-hour expiration
- **Password Hashing**: bcrypt with cost factor 12
- **User Isolation**: Database-level multi-tenant isolation
- **Secure Sessions**: HTTP-only cookies for token storage

---

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI 0.125+** | High-performance Python web framework |
| **SQLModel 0.0.14+** | Type-safe ORM combining SQLAlchemy + Pydantic |
| **Neon PostgreSQL** | Serverless PostgreSQL database |
| **OpenAI SDK** | AI/LLM integration for chat functionality |
| **MCP Protocol** | Model Context Protocol for tool invocation |
| **Alembic** | Database migrations |
| **python-jose** | JWT token handling |
| **passlib + bcrypt** | Secure password hashing |
| **uv** | Fast Python package manager |

### Frontend

| Technology | Purpose |
|------------|---------|
| **Next.js 16** | React framework with App Router |
| **TypeScript 5.x** | Type-safe JavaScript (strict mode) |
| **Tailwind CSS 4** | Utility-first CSS framework |
| **shadcn/ui** | Accessible UI components (Radix UI) |
| **Lucide Icons** | Beautiful icon library |
| **next-themes** | Dark/light theme support |
| **Sonner** | Toast notifications |
| **pnpm** | Fast, efficient package manager |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Kubernetes** | Container orchestration |
| **Helm** | Kubernetes package manager |
| **Dapr** | Microservices runtime (pub/sub, state) |
| **Redis** | State store for Dapr |
| **Minikube** | Local Kubernetes development |

---

## Architecture

```
                              ┌─────────────────────────────────────────┐
                              │              Load Balancer              │
                              └──────────────────┬──────────────────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                    ▼                            ▼                            ▼
         ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
         │     Frontend     │       │     Backend      │       │    API Docs      │
         │    (Next.js)     │──────▶│    (FastAPI)     │       │    (Swagger)     │
         │   Port: 3000     │       │   Port: 8000     │       │   /docs /redoc   │
         └──────────────────┘       └────────┬─────────┘       └──────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
         ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
         │   PostgreSQL     │    │   OpenAI API     │    │   Dapr Sidecar   │
         │     (Neon)       │    │    (MCP Tools)   │    │    (Pub/Sub)     │
         └──────────────────┘    └──────────────────┘    └────────┬─────────┘
                                                                  │
                         ┌────────────────────────────────────────┼────────────────────────────────────────┐
                         │                                        │                                        │
                         ▼                                        ▼                                        ▼
              ┌──────────────────┐                     ┌──────────────────┐                     ┌──────────────────┐
              │  Notification    │                     │    Recurring     │                     │      Redis       │
              │    Service       │                     │     Service      │                     │  (State Store)   │
              │  (Reminders)     │                     │ (Task Scheduler) │                     │                  │
              └──────────────────┘                     └──────────────────┘                     └──────────────────┘
```

### Monorepo Structure

```
phase-5/
├── backend/                    # FastAPI REST API
│   ├── src/
│   │   ├── api/               # Route handlers (auth, tasks, chat, conversations)
│   │   ├── models/            # SQLModel entities (User, Task, Tag, Conversation, Message)
│   │   ├── services/          # Business logic + reminder scheduler
│   │   ├── mcp/               # AI agent and MCP tool definitions
│   │   ├── core/              # Config, security, database setup
│   │   └── middleware/        # Logging, error handling, correlation ID
│   ├── alembic/               # Database migrations
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/                   # Next.js Web Application
│   ├── src/
│   │   ├── app/               # App Router pages (home, auth, dashboard)
│   │   ├── components/
│   │   │   ├── chat/          # CUI components (ChatLayout, Sidebar, Messages)
│   │   │   ├── tasks/         # GUI components (TaskList, TaskForm, Filters)
│   │   │   ├── navigation/    # Header, mode toggle
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── lib/               # API client, utilities
│   │   └── types/             # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
│
├── notification-service/       # Reminder Microservice
│   ├── src/
│   │   ├── api/               # Health and reminder endpoints
│   │   ├── handlers/          # CloudEvent handlers
│   │   └── core/              # Config, logging
│   └── Dockerfile
│
├── recurring-service/          # Recurring Tasks Microservice
│   ├── src/
│   │   ├── api/               # Health and event endpoints
│   │   ├── handlers/          # Task completion handlers
│   │   ├── services/          # Recurrence calculation
│   │   └── core/              # Config, logging
│   └── Dockerfile
│
├── dapr/                       # Dapr Configuration
│   └── components/            # Pub/sub, state store configs
│
├── helm/                       # Kubernetes Deployment
│   └── taskai/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── scripts/                    # Deployment Scripts
│   ├── deploy-minikube.sh     # Linux/Mac deployment
│   ├── deploy-minikube.ps1    # Windows deployment
│   └── verify-deployment.*    # Verification scripts
│
├── specs/                      # Feature Specifications (SDD)
│   ├── 001-todo-app-baseline/
│   ├── 002-todo-ai-chatbot/
│   ├── 003-combined-cui-gui/
│   └── 004-phase5-cloud-deployment/
│
├── docker-compose.yml          # Local Docker deployment
├── .env.example                # Environment template
└── .specify/                   # Spec-Kit Plus configuration
```

---

## Getting Started

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend runtime |
| **uv** | Latest | Python package manager |
| **pnpm** | Latest | Node package manager |
| **PostgreSQL** | - | Neon serverless account |
| **OpenAI API Key** | - | AI functionality |

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/AsharibAli/taskai.git
cd taskai
```

#### 2. Backend Setup

```bash
cd backend

# Install dependencies (creates .venv automatically)
uv sync

# Configure environment
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Security
JWT_SECRET=your-super-secure-random-string-min-32-chars

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4.1-2025-04-14
```

Run migrations and start the server:

```bash
# Apply database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn src.main:app --reload --port 8000
```

Backend available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
pnpm dev
```

Frontend available at: `http://localhost:3000`

---

## Deployment

### Option 1: Docker Compose (Local)

Quick deployment with all services containerized:

```bash
# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and JWT_SECRET

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | (internal) |

### Option 2: Kubernetes (Minikube)

Production-like deployment using Helm:

```bash
# Linux/Mac
./scripts/deploy-minikube.sh

# Windows PowerShell
.\scripts\deploy-minikube.ps1

# Verify deployment
kubectl get pods -n taskai
```

#### Manual Kubernetes Deployment

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Configure Docker to use Minikube's daemon
eval $(minikube docker-env)  # Linux/Mac
# OR
minikube docker-env --shell powershell | Invoke-Expression  # Windows

# Build images
docker build -t taskai-backend:latest ./backend
docker build --build-arg NEXT_PUBLIC_API_URL="http://localhost:30800" \
  -t taskai-frontend:latest ./frontend

# Deploy with Helm
helm upgrade --install taskai ./helm/taskai \
  --namespace taskai \
  --create-namespace \
  --set secrets.openaiApiKey="sk-your-key"

# Get Minikube IP
minikube ip
```

| Service | URL |
|---------|-----|
| Frontend | http://\<minikube-ip\>:30300 |
| Backend API | http://\<minikube-ip\>:30800 |
| Swagger Docs | http://\<minikube-ip\>:30800/docs |

#### Useful Kubernetes Commands

```bash
# View all pods
kubectl get pods -n taskai

# View logs
kubectl logs -f deploy/taskai-backend -n taskai

# Open Minikube dashboard
minikube dashboard

# Uninstall
helm uninstall taskai -n taskai
kubectl delete namespace taskai
```

---

## API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login and get JWT token |
| `/api/auth/me` | GET | Get current user profile |

### Tasks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks` | GET | List tasks (with filters) |
| `/api/tasks` | POST | Create new task |
| `/api/tasks/{id}` | GET | Get task by ID |
| `/api/tasks/{id}` | PUT | Update task |
| `/api/tasks/{id}` | DELETE | Delete task |
| `/api/tasks/{id}/tags` | POST | Add tag to task |
| `/api/tasks/{id}/tags/{tag}` | DELETE | Remove tag |
| `/api/tasks/search` | GET | Full-text search |

#### Task Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `priority` | string | Filter: high, medium, low |
| `is_completed` | boolean | Filter: true, false |
| `tag` | string | Filter by tag name |
| `overdue` | boolean | Show only overdue tasks |
| `sort_by` | string | Sort: due_date, priority, created_at |
| `sort_order` | string | Order: asc, desc |

### Chat (CUI)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/chat` | POST | Send message to AI |
| `/api/conversations` | GET | List conversations |
| `/api/conversations` | POST | Create conversation |
| `/api/conversations/{id}` | GET | Get conversation with messages |
| `/api/conversations/{id}` | DELETE | Delete conversation |

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Environment Variables

### Backend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET` | Yes | Secret for JWT signing (min 32 chars) |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `OPENAI_MODEL` | No | Model name (default: gpt-4.1-2025-04-14) |
| `CORS_ORIGINS` | No | Allowed origins (default: localhost) |

### Frontend (.env.local)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |

---

## Development

### Spec-Driven Development (SDD)

This project follows strict SDD principles using Spec-Kit Plus:

1. **Specification First**: No code before approved specs
2. **Implementation Planning**: Architecture decisions documented
3. **Task Breakdown**: Testable tasks with acceptance criteria
4. **Controlled Implementation**: Changes via defined workflow

### Available Commands

```bash
# Specification
/sp.specify    # Create feature specification
/sp.clarify    # Clarify underspecified areas
/sp.plan       # Create implementation plan
/sp.tasks      # Generate task breakdown
/sp.implement  # Execute implementation
/sp.analyze    # Cross-artifact analysis
/sp.adr        # Create Architecture Decision Record
```

### Project Specifications

| Spec | Description |
|------|-------------|
| `001-todo-app-baseline` | Core todo functionality |
| `002-todo-ai-chatbot` | AI chat integration |
| `003-combined-cui-gui` | Dual interface |
| `004-phase5-cloud-deployment` | Cloud infrastructure |

---

## Security

### Authentication Flow

1. User registers with email/password
2. Password hashed with bcrypt (cost 12)
3. JWT token issued on login (24h expiry)
4. Token validated on each protected request
5. User ID extracted from JWT for data isolation

### Security Measures

- **No secrets in code**: All via environment variables
- **HTTPS in production**: SSL/TLS enforced
- **User isolation**: Database-level tenant separation
- **Input validation**: Pydantic schemas on all endpoints
- **MCP tool safety**: user_id always from JWT, never user input

---

## Contributing

Contributions must follow the SDD workflow:

1. **Fork** the repository
2. **Create specification** (`/sp.specify`)
3. **Plan implementation** (`/sp.plan`)
4. **Generate tasks** (`/sp.tasks`)
5. **Implement changes** (`/sp.implement`)
6. **Submit PR** with spec artifacts

See `.specify/` for templates and guidelines.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [OpenAI](https://openai.com/) - AI/LLM capabilities
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [Dapr](https://dapr.io/) - Microservices runtime
- [Spec-Kit Plus](https://github.com/spec-kit/spec-kit-plus) - SDD framework

---

<p align="center">
  Built with Spec-Driven Development
</p>
