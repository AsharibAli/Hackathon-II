# Advanced Todo Application with CUI & GUI

A modern, secure, multi-user todo application featuring **dual interfaces** - Conversational User Interface (CUI) and Graphical User Interface (GUI). Built with **spec-driven development** principles.

## Key Features

- **Dual Interface** - Choose how you work:
  - **CUI (Conversational)**: ChatGPT-style natural language task management
  - **GUI (Graphical)**: Traditional forms, buttons, and checkboxes
- **Seamless Switching** - Toggle between modes anytime; your tasks stay in sync
- **AI-Powered** - Natural language understanding via OpenAI for CUI mode
- **Multi-User Isolation** - Each user's tasks and conversations are private
- **Real-Time Sync** - Tasks created in one mode appear instantly in the other

## Architecture

**Monorepo Structure:**
- `backend/` - FastAPI (Python) REST API with JWT authentication & AI agent
- `frontend/` - Next.js 16 (TypeScript) with dual-mode interface
- `specs/` - Feature specifications and design documents
- `.specify/` - Spec-Kit Plus configuration and templates

## Tech Stack

### Backend
- **Framework:** FastAPI 0.125+
- **ORM:** SQLModel 0.0.14+
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** JWT (python-jose)
- **AI:** OpenAI Agents SDK + MCP Tools
- **Password Hashing:** bcrypt (passlib)
- **Package Manager:** uv

### Frontend
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript 5.x (strict mode)
- **Styling:** Tailwind CSS 4
- **UI Components:** shadcn/ui (Radix UI)
- **Notifications:** Sonner
- **Package Manager:** pnpm

## Features

### CUI Mode (Conversational User Interface)
- Natural language task creation ("Add a task to buy groceries")
- Ask to see your tasks ("Show me my tasks")
- Complete tasks via chat ("Mark buy groceries as done")
- Update and delete tasks conversationally
- Conversation history persistence
- Multi-turn context awareness

### GUI Mode (Graphical User Interface)
- Task creation form with title and description
- Task list with checkboxes for completion
- Edit tasks via dialog modal
- Delete tasks with confirmation
- Visual completion status (strikethrough)
- Loading states and error handling

### Shared Features
- JWT-based authentication
- Secure registration and login
- User profile management
- Responsive design (mobile + desktop)
- Toast notifications for feedback
- Error boundaries for stability

## Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **uv** (Python package manager): `pip install uv`
- **pnpm** (Node package manager): `npm install -g pnpm`
- **Neon PostgreSQL account**: Sign up at https://neon.tech
- **OpenAI API Key**: For CUI mode AI functionality

## Deployment Options

### Option 1: Local Development
See [specs/003-combined-cui-gui/quickstart.md](specs/003-combined-cui-gui/quickstart.md) for detailed setup instructions.

### Option 2: Docker Compose
Quick local deployment with all services containerized:

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and JWT_SECRET

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Option 3: Kubernetes (Minikube)
Production-like deployment using Helm charts:

```bash
# Deploy to Minikube (Linux/Mac)
./scripts/deploy-minikube.sh --openai-key "sk-your-key"

# Deploy to Minikube (Windows PowerShell)
.\scripts\deploy-minikube.ps1 -OpenAIKey "sk-your-key"

# Verify deployment
./scripts/verify-deployment.sh  # or .ps1 for Windows
```

See [Kubernetes Deployment](#kubernetes-deployment) section for details.

## Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies (creates .venv automatically)
uv sync

# Configure environment
cp .env.example .env
# Edit .env with:
# - DATABASE_URL (Neon PostgreSQL connection string)
# - JWT_SECRET (secure random string)
# - OPENAI_API_KEY (your OpenAI API key)

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn src.main:app --reload --port 8000
```

Backend will be available at http://localhost:8000
API docs at http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies with pnpm
pnpm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
pnpm dev
```

Frontend will be available at http://localhost:3000

## Project Structure

```
phase-4/
├── backend/
│   ├── src/
│   │   ├── models/          # SQLModel entities (User, Task, Conversation, Message)
│   │   ├── services/        # Business logic
│   │   ├── api/             # FastAPI endpoints (auth, tasks, chat, conversations)
│   │   ├── mcp/             # AI agent and MCP tools
│   │   ├── core/            # Configuration, security, database
│   │   └── middleware/      # Logging, error handling
│   ├── alembic/             # Database migrations
│   ├── Dockerfile           # Backend container image
│   └── pyproject.toml       # uv dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/
│   │   │   ├── chat/        # CUI components (ChatLayout, Sidebar, etc.)
│   │   │   ├── tasks/       # GUI components (TaskList, TaskForm, etc.)
│   │   │   ├── navigation/  # Mode toggle, app header
│   │   │   └── ui/          # shadcn/ui components
│   │   ├── lib/             # API client, utilities
│   │   └── types/           # TypeScript interfaces
│   ├── Dockerfile           # Frontend container image
│   └── package.json         # pnpm dependencies
├── helm/
│   └── taskai/              # Helm chart for Kubernetes deployment
│       ├── Chart.yaml       # Chart metadata
│       ├── values.yaml      # Configuration values
│       └── templates/       # Kubernetes manifests
├── scripts/
│   ├── deploy-minikube.sh   # Minikube deployment (Linux/Mac)
│   ├── deploy-minikube.ps1  # Minikube deployment (Windows)
│   ├── verify-deployment.sh # Deployment verification (Linux/Mac)
│   └── verify-deployment.ps1# Deployment verification (Windows)
├── specs/
│   ├── 001-todo-app-baseline/    # Phase-2 baseline spec
│   ├── 002-todo-ai-chatbot/      # Phase-3 AI chatbot spec
│   └── 003-combined-cui-gui/     # Phase-4 combined CUI+GUI spec
├── docker-compose.yml       # Docker Compose for local deployment
├── .env.example             # Environment variables template
└── .specify/                # Spec-Kit Plus configuration
```

## How It Works

### Dual Mode Navigation
1. Log in to see the main application
2. Use the **Chat** / **Tasks** toggle in the header
3. Switch modes anytime - your data syncs automatically

### CUI Mode
```
You: "Add a task to buy groceries"
AI: "I've created a new task 'buy groceries' for you!"

You: "Show me my tasks"
AI: "You have 3 tasks:
     1. buy groceries (pending)
     2. call mom (completed)
     3. finish report (pending)"

You: "Mark buy groceries as done"
AI: "Done! I've marked 'buy groceries' as completed."
```

### GUI Mode
- Click the "Tasks" tab to switch
- Use the form to add new tasks
- Check the checkbox to complete tasks
- Click edit/delete icons for more actions

## API Documentation

Once the backend is running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login user |
| `/api/tasks` | GET | Get all tasks (GUI) |
| `/api/tasks` | POST | Create task (GUI) |
| `/api/chat/chat` | POST | Send chat message (CUI) |
| `/api/conversations` | GET | List conversations (CUI) |

## Security

- JWT tokens for authentication (24-hour expiration)
- Bcrypt password hashing (cost factor 12)
- Multi-user isolation at database and API layers
- HTTPS required in production
- No secrets in code (all via environment variables)
- MCP tools enforce user_id from JWT (never from user input)

## Constitution & Principles

This project follows strict **Spec-Driven Development (SDD)** principles:

1. **Spec-First Development**: No code before approved specifications
2. **Single Code Authority**: Only Claude Code writes implementation
3. **Separation of Concerns**: Clear backend/frontend/CUI/GUI boundaries
4. **Authentication Enforcement**: JWT on all protected endpoints
5. **Stateless Server**: No in-memory state; all data in PostgreSQL
6. **Tool-Driven AI**: CUI operations only through MCP tools

See `.specify/memory/constitution.md` for complete governance rules.

## Documentation

- **Combined Feature Spec**: `specs/003-combined-cui-gui/spec.md`
- **Implementation Plan**: `specs/003-combined-cui-gui/plan.md`
- **Task Breakdown**: `specs/003-combined-cui-gui/tasks.md`
- **Data Model**: `specs/003-combined-cui-gui/data-model.md`
- **Setup Guide**: `specs/003-combined-cui-gui/quickstart.md`

## Kubernetes Deployment

### Prerequisites

- **minikube** - Local Kubernetes cluster
- **kubectl** - Kubernetes CLI
- **helm** - Kubernetes package manager
- **docker** - Container runtime

### Quick Deploy

```bash
# Linux/Mac
./scripts/deploy-minikube.sh --openai-key "sk-your-key"

# Windows PowerShell
.\scripts\deploy-minikube.ps1 -OpenAIKey "sk-your-key"
```

### Manual Deployment

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Configure Docker to use Minikube's daemon
eval $(minikube docker-env)  # Linux/Mac
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

# Verify deployment
kubectl get pods -n taskai
```

### Access URLs

| Service | URL |
|---------|-----|
| Frontend | http://\<minikube-ip\>:30300 |
| Backend API | http://\<minikube-ip\>:30800 |
| Swagger Docs | http://\<minikube-ip\>:30800/docs |

Get Minikube IP: `minikube ip`

Or use `minikube tunnel` for localhost access.

### Helm Values

Key configuration options in `helm/taskai/values.yaml`:

```yaml
secrets:
  jwtSecret: "your-jwt-secret"
  openaiApiKey: "sk-your-key"

frontend:
  service:
    nodePort: 30300

backend:
  service:
    nodePort: 30800
  env:
    OPENAI_MODEL: "gpt-4.1-2025-04-14"
```

### Useful Commands

```bash
# View pods
kubectl get pods -n taskai

# View logs
kubectl logs -f deploy/taskai-backend -n taskai

# Describe pod
kubectl describe pod <pod-name> -n taskai

# Open Minikube dashboard
minikube dashboard

# Uninstall
helm uninstall taskai -n taskai
kubectl delete namespace taskai
```

## Docker Compose

For local development without Kubernetes:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | Next.js web application |
| backend | 8000 | FastAPI REST API |
| postgres | 5432 | PostgreSQL database |

## License

[Specify your license here]

## Contributing

This project uses Spec-Kit Plus for spec-driven development. All contributions must:
1. Start with a specification (`/sp.specify`)
2. Create an implementation plan (`/sp.plan`)
3. Generate tasks (`/sp.tasks`)
4. Only then implement (`/sp.implement`)

See `.specify/` for templates and guidelines.
