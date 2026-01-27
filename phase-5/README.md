<p align="center">
  <img src="frontend/public/favicon.svg" height="100" alt="TaskAI Logo" />
</p>

<h1 align="center">TaskAI - Organize your life, your way</h1>

<p align="center">
  A production-ready, event-driven, AI-powered task management platform featuring conversational AI (CUI) and traditional graphical UI (GUI) interfaces.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16+-black?style=for-the-badge&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.125+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Kafka-3.6-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white" alt="Kafka" />
  <img src="https://img.shields.io/badge/Kubernetes-1.28+-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes" />
  <img src="https://img.shields.io/badge/Dapr-1.12+-0D2192?style=for-the-badge&logo=dapr&logoColor=white" alt="Dapr" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenAI-GPT--4.1-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/MCP-Tools-00A67E?style=for-the-badge" alt="MCP" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Production](#-production)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

TaskAI is a next-generation task management system that combines the power of AI with a robust microservices architecture. It offers users two distinct ways to interact with their tasks:

### **Dual Interface Design**

#### 🤖 **Chat Mode (Conversational UI)**
Interact with your tasks using natural language powered by OpenAI's GPT-4.1 through the Model Context Protocol (MCP). The AI understands context, interprets intent, and executes actions through 18 specialized tools.

```
👤 You: "Add a high priority task to review the quarterly report by Friday"
🤖 AI:  "Done! I've created 'Review quarterly report' with high priority, due Friday."

👤 You: "Show me my overdue tasks"
🤖 AI:  "You have 2 overdue tasks:
        1. Submit expense report (high priority, due Dec 20)
        2. Reply to client email (medium priority, due Dec 22)"

👤 You: "Mark the expense report as done"
🤖 AI:  "✓ Marked 'Submit expense report' as completed."
```

#### 📊 **Tasks Mode (Graphical UI)**
Traditional visual interface with advanced filtering, sorting, and organization capabilities. Both interfaces sync in real-time, allowing seamless transitions between modes.

### **Cloud-Native Microservices**

TaskAI is built as a distributed system with:
- **4 independent microservices** (Backend API, Frontend, Notification Service, Recurring Service)
- **Event-driven architecture** using Kafka pub/sub via Dapr
- **Kubernetes-native deployment** with Helm charts
- **Horizontal scalability** with stateless service design
- **Production-grade observability** (OpenTelemetry, Prometheus, structured logging)

---

## ✨ Key Features

### 🎯 **Task Management**

| Feature             | Description                                                    |
| ------------------- | -------------------------------------------------------------- |
| **CRUD Operations** | Complete Create, Read, Update, Delete with user isolation      |
| **Priority Levels** | Low, Medium, High priority with visual indicators              |
| **Due Dates**       | Natural language date parsing ("tomorrow", "next Friday")      |
| **Reminders**       | Background scheduler for email notifications                   |
| **Recurring Tasks** | Daily, Weekly, Monthly patterns with automatic creation        |
| **Tags**            | Organize tasks with reusable, case-insensitive tags            |
| **Search**          | Full-text search across titles and descriptions                |
| **Filtering**       | Multi-criteria filtering (priority, tags, completion, overdue) |
| **Sorting**         | Sort by created date, due date, priority, title                |

### 🤖 **AI-Powered Chat Interface**

**18 MCP Tools Available:**

| Category                | Tools                                                                   |
| ----------------------- | ----------------------------------------------------------------------- |
| **Core Operations**     | `add_task`, `list_tasks`, `complete_task`, `update_task`, `delete_task` |
| **Priority Management** | `set_priority`, `filter_by_priority`                                    |
| **Tag Management**      | `add_tag`, `remove_tag`, `filter_by_tag`                                |
| **Due Date Management** | `set_due_date`, `show_overdue`                                          |
| **Search & Filter**     | `search_tasks`, `combined_filter`, `sort_tasks`                         |
| **Reminders**           | `set_reminder`                                                          |
| **Recurrence**          | `set_recurrence`                                                        |

**Natural Language Understanding:**
- "Show me high priority tasks due this week"
- "Create a recurring task for weekly team standup"
- "Move all design tasks to high priority"
- "Find tasks mentioning client meeting"

### 🔄 **Event-Driven Architecture**

```
Backend API
    ↓ (publishes)
Kafka Topics (task-events, reminders)
    ↓ (consumes)
├── Recurring Service → Creates next task instance
└── Notification Service → Sends email reminders
```

**Event Topics:**
- `task-events`: Task lifecycle events (created, updated, completed, deleted)
- `reminders`: Reminder notifications for tasks

**Event Handlers:**
- **Recurring Service**: Listens to task.completed, creates next occurrence for recurring tasks
- **Notification Service**: Listens to reminders, sends email notifications via Resend

### 🔐 **Security & Authentication**

- **JWT-based authentication** with bcrypt password hashing (12 rounds)
- **User isolation** - All data scoped to authenticated user
- **Secure token management** with 24-hour expiration
- **CORS configuration** for cross-origin requests
- **Environment-based secrets** (never committed to git)

### 📊 **Observability & Monitoring**

- **OpenTelemetry tracing** across all services
- **Prometheus metrics** for request/response monitoring
- **Structured JSON logging** with correlation IDs
- **Distributed tracing** through Dapr sidecars
- **Health check endpoints** for Kubernetes probes

---

## 🏗️ Architecture

### **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│  ┌──────────────┐                        ┌──────────────────┐  │
│  │   Chat UI    │                        │    Tasks UI      │  │
│  │   (CUI Mode) │                        │   (GUI Mode)     │  │
│  └──────┬───────┘                        └────────┬─────────┘  │
│         │                                          │            │
│         └──────────────────┬───────────────────────┘            │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTPS/REST API
┌────────────────────────────┼────────────────────────────────────┐
│                            ▼                                    │
│                  ┌─────────────────┐                            │
│                  │   Backend API   │                            │
│                  │    (FastAPI)    │                            │
│                  │                 │                            │
│                  │  ┌───────────┐  │                            │
│                  │  │  Chat     │  │  - JWT Auth                │
│                  │  │  Agent    │  │  - Task CRUD               │
│                  │  │  (MCP)    │  │  - Event Publishing        │
│                  │  └───────────┘  │  - Reminder Scheduler      │
│                  │                 │                            │
│                  │  ┌───────────┐  │                            │
│                  │  │  Event    │  │                            │
│                  │  │ Publisher │  │                            │
│                  │  └─────┬─────┘  │                            │
│                  └────────┼─────────┘                            │
│                           │                                     │
│              ┌────────────┼────────────┐                        │
│              │   Dapr Sidecar (daprd)  │                        │
│              └────────────┼────────────┘                        │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                  Kafka Pub/Sub (via Dapr)                     │
│  Topics: task-events, reminders                               │
└────────┬──────────────────────────────────────┬───────────────┘
         │                                      │
         ▼                                      ▼
┌──────────────────────┐            ┌──────────────────────────┐
│  Recurring Service   │            │  Notification Service     │
│                      │            │                          │
│  - Task Completed    │            │  - Reminder Handler      │
│  - Calculate Next    │            │  - Email Sending         │
│  - Create Instance   │            │  - Resend API            │
│                      │            │                          │
│  Dapr Sidecar        │            │  Dapr Sidecar            │
└──────────────────────┘            └──────────────────────────┘
         │
         └─────────► Backend API (Create Task)

┌───────────────────────────────────────────────────────────────┐
│                      Data Layer                               │
│  ┌────────────────┐           ┌────────────────┐             │
│  │  PostgreSQL 16 │           │  State Store   │             │
│  │                │           │  (Dapr/PG)     │             │
│  │  - Users       │           └────────────────┘             │
│  │  - Tasks       │                                           │
│  │  - Tags        │                                           │
│  │  - Conversations│                                          │
│  │  - Messages    │                                           │
│  └────────────────┘                                           │
└───────────────────────────────────────────────────────────────┘
```

### **Microservices Breakdown**

| Service                  | Port | Purpose                                                   | Tech Stack                                      |
| ------------------------ | ---- | --------------------------------------------------------- | ----------------------------------------------- |
| **Frontend**             | 3000 | User interface (Chat + Tasks UI)                          | Next.js 16, TypeScript, Tailwind CSS, Shadcn/ui |
| **Backend API**          | 8000 | Core business logic, authentication, task management      | FastAPI, SQLModel, PostgreSQL, OpenAI, MCP      |
| **Recurring Service**    | 8002 | Process task.completed events, create recurring instances | FastAPI, Dapr subscriber                        |
| **Notification Service** | 8001 | Send reminder notifications via email                     | FastAPI, Resend API, Dapr subscriber            |

### **Data Model (PostgreSQL)**

```sql
-- Core Tables
users (id, email, hashed_password, full_name, profile_picture, created_at, updated_at)
tasks (id, user_id, title, description, is_completed, priority, due_date,
       remind_at, reminder_sent, recurrence, parent_task_id, created_at, updated_at)
tags (id, user_id, name, created_at)
task_tags (task_id, tag_id)  -- Many-to-many junction

-- Chat Tables
conversations (id, user_id, title, created_at, updated_at)
messages (id, conversation_id, role, content, created_at)

-- Indexes
- users(email) UNIQUE
- tasks(user_id, is_completed)
- tasks(user_id, due_date) for overdue queries
- tags(user_id, name) UNIQUE together
```

---

## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI 0.125+ (Python 3.11+)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL 16 (Neon for cloud, local for dev)
- **Authentication**: JWT (python-jose) + bcrypt
- **AI/LLM**: OpenAI API (GPT-4.1-2025-04-14)
- **MCP**: Model Context Protocol for tool integration
- **Event Bus**: Kafka 3.6 (KRaft mode) via Dapr
- **Email**: Resend API for notifications
- **Scheduling**: APScheduler for background tasks
- **Observability**:
  - OpenTelemetry (tracing)
  - Prometheus (metrics)
  - Structlog (structured logging)

### **Frontend**
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.x
- **UI Components**: Shadcn/ui (Radix UI primitives)
- **Fonts**: Cormorant Garamond, DM Sans, JetBrains Mono
- **State Management**: React hooks + context
- **API Client**: Native fetch with custom error handling
- **Package Manager**: pnpm 9.x

### **Infrastructure**
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes 1.28+
- **Package Manager**: Helm 3.x
- **Service Mesh**: Dapr 1.12+ (pub/sub, state management)
- **Message Queue**: Apache Kafka 3.6
- **Ingress**: Nginx Ingress Controller
- **Cloud Providers**: DigitalOcean Kubernetes (DOK), supports AKS, GKE, EKS

### **Development Tools**
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions (planned)
- **Testing**: pytest (backend), Jest (frontend - planned)
- **Linting**: ESLint (frontend), Black (backend - planned)
- **API Testing**: httpx (backend integration tests)

---

## 🚀 Quick Start

### **Prerequisites**

- **Docker** 20.10+ & **Docker Compose** 2.x
- **Node.js** 18+ with **pnpm** 9+
- **Python** 3.11+
- **OpenAI API Key** (for Chat Mode)

### **Local Development Setup**

#### **1. Clone Repository**

```bash
git clone https://github.com/AsharibAli/Hackathon-II.git
cd Hackathon-II/phase-5
```

#### **2. Environment Configuration**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values:
# - JWT_SECRET: Generate with `openssl rand -hex 32`
# - OPENAI_API_KEY: Get from https://platform.openai.com
# - POSTGRES_PASSWORD: Set a secure password
```

**Required Environment Variables:**
```bash
# Database (auto-configured for docker-compose)
POSTGRES_PASSWORD=taskai_secret

# Authentication
JWT_SECRET=your-super-secret-jwt-key-min-32-chars

# OpenAI (for Chat Mode)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4.1-2025-04-14

# Email (Optional - for reminders)
RESEND_API_KEY=re_your_resend_api_key
RESEND_FROM_EMAIL=onboarding@resend.dev
```

#### **3. Start Services**

```bash
# Start all services (Backend, Frontend, PostgreSQL, Kafka, Dapr)
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Services will be available at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)
- PostgreSQL: localhost:9432
- Kafka: localhost:9092

#### **4. Create First User**

```bash
# Option 1: Via Frontend UI
# Go to http://localhost:3000/register

# Option 2: Via API (curl)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

#### **5. Start Using TaskAI**

1. **Login** at http://localhost:3000/login
2. **Switch to Chat Mode** (toggle at top)
3. **Try AI commands**:
   - "Create a task to buy groceries"
   - "Show me all high priority tasks"
   - "Mark task 'buy groceries' as done"
4. **Switch to Tasks Mode** (toggle at top)
5. **Use GUI** to filter, sort, and manage tasks visually

---

## 🚢 Deployment

### **Production Deployment Options**

TaskAI supports multiple deployment strategies:

#### **1. Kubernetes with Helm (Recommended for Production)**

**Prerequisites:**
- Kubernetes cluster (DOK, AKS, GKE, EKS, or Minikube)
- `kubectl` configured with cluster access
- `helm` 3.x installed
- `doctl` (for DigitalOcean) or cloud provider CLI

**Deployment Steps:**

```bash
# 1. Configure kubectl for your cluster
# For DigitalOcean:
doctl kubernetes cluster kubeconfig save your-cluster-name

# 2. Create namespace
kubectl create namespace todo-app

# 3. Create secrets (Kafka credentials, JWT secret, etc.)
kubectl create secret generic kafka-credentials \
  --from-literal=brokers=your-kafka-broker:25073 \
  --from-literal=username=your-kafka-user \
  --from-literal=password=your-kafka-password \
  -n todo-app

kubectl create secret generic app-secrets \
  --from-literal=jwt-secret=$(openssl rand -hex 32) \
  --from-literal=openai-api-key=sk-your-key \
  -n todo-app

# 4. Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  --namespace todo-app \
  --set global.domain=yourdomain.com \
  --set backend.image.tag=1.0.0 \
  --set frontend.image.tag=1.0.0

# 5. Apply Dapr components
kubectl apply -f dapr/deployment/01-kafka-pubsub-component.yaml
kubectl apply -f dapr/deployment/02-subscription-task-events.yaml
kubectl apply -f dapr/deployment/03-subscription-reminders.yaml

# 6. Check deployment status
kubectl get pods -n todo-app
kubectl get services -n todo-app
```

**Enable Dapr for Event-Driven Features:**

```bash
# Deploy with Dapr sidecars enabled
helm upgrade todo-chatbot ./helm/todo-chatbot \
  -n todo-app \
  -f helm/todo-chatbot/helm-values-dapr-enabled.yaml
```

#### **2. Automated Deployment Scripts**

Use the provided deployment scripts for quick deployments:

```bash
# Deploy all services at once
./scripts/deploy-all.sh v1.0.5

# Deploy individual services
./scripts/deploy-backend.sh v1.0.5
./scripts/deploy-frontend.sh v1.0.5
./scripts/deploy-recurring-service.sh v1.0.5
./scripts/deploy-notification-service.sh v1.0.5

# Deploy with specific services
./scripts/deploy-all.sh --services=backend,frontend
```

**Script Features:**
- Builds Docker images locally
- Pushes to DigitalOcean Container Registry
- Updates Kubernetes deployments
- Waits for rollout completion
- Verifies Dapr sidecar status
- Shows deployment summary

For detailed deployment documentation, see [scripts/README.md](scripts/README.md).

#### **3. Docker Compose (Simple Deployment)**

For small-scale deployments without Kubernetes:

```bash
# Production docker-compose with external services
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale backend=3
```

### **Production Checklist**

- [ ] Set strong JWT_SECRET (32+ characters)
- [ ] Use managed PostgreSQL (Neon, AWS RDS, etc.)
- [ ] Use managed Kafka (DigitalOcean, Confluent Cloud, AWS MSK)
- [ ] Configure CORS_ORIGINS for your domain
- [ ] Enable HTTPS with TLS certificates (Let's Encrypt)
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation (ELK stack, Loki)
- [ ] Enable auto-scaling (HPA for Kubernetes)
- [ ] Set up backups for PostgreSQL
- [ ] Configure health checks and readiness probes
- [ ] Set resource limits (CPU, memory) for pods
- [ ] Enable Dapr for event-driven features
- [ ] Configure email service (Resend API key)

---

## 📚 API Documentation

### **Interactive API Docs**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Authentication Endpoints**

```bash
# Register new user
POST /api/auth/register
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}

# Login
POST /api/auth/login
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepassword"
}
Response: { "access_token": "eyJ...", "user": {...} }

# Logout
POST /api/auth/logout
Authorization: Bearer {token}
```

### **Task Management Endpoints**

```bash
# List tasks with filters
GET /api/tasks?priority=high&is_completed=false&tag=work

# Create task
POST /api/tasks
Authorization: Bearer {token}
Content-Type: application/json
{
  "title": "Complete project proposal",
  "description": "Write and submit Q1 proposal",
  "priority": "high",
  "due_date": "2025-02-01T17:00:00Z",
  "recurrence": "none",
  "tags": ["work", "urgent"]
}

# Get single task
GET /api/tasks/{task_id}

# Update task
PUT /api/tasks/{task_id}
{
  "title": "Updated title",
  "priority": "medium"
}

# Toggle completion
PATCH /api/tasks/{task_id}/complete

# Delete task
DELETE /api/tasks/{task_id}

# Search tasks
GET /api/tasks/search?q=project

# Add tag
POST /api/tasks/{task_id}/tags
{ "tag_name": "important" }

# Remove tag
DELETE /api/tasks/{task_id}/tags/{tag_name}

# Set reminder
POST /api/tasks/{task_id}/reminder
{ "remind_at": "2025-01-25T09:00:00Z" }
```

### **Chat Endpoints**

```bash
# Send message to AI
POST /api/chat/chat
Authorization: Bearer {token}
Content-Type: application/json
{
  "message": "Show me all high priority tasks",
  "conversation_id": "optional-uuid"
}
Response: {
  "response": "Here are your high priority tasks: ...",
  "conversation_id": "uuid",
  "user_message_id": "uuid",
  "assistant_message_id": "uuid"
}

# Get conversations
GET /api/chat/conversations
Authorization: Bearer {token}
```

### **Response Formats**

**Success Response:**
```json
{
  "id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "is_completed": false,
  "priority": "high",
  "due_date": "2025-02-01T17:00:00Z",
  "remind_at": null,
  "reminder_sent": false,
  "recurrence": "none",
  "tags": ["work", "urgent"],
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```

**Error Response:**
```json
{
  "detail": "Task not found"
}
```

---

## 📁 Project Structure

```
phase-5/
├── backend/                      # FastAPI backend service
│   ├── src/
│   │   ├── api/                  # API route handlers
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── tasks.py         # Task CRUD endpoints (476 lines)
│   │   │   └── chat.py          # Chat/AI endpoints
│   │   ├── core/                 # Core configuration
│   │   │   ├── config.py        # Environment settings
│   │   │   ├── database.py      # SQLModel setup
│   │   │   └── security.py      # JWT & bcrypt
│   │   ├── models/               # Database models
│   │   │   ├── user.py          # User model
│   │   │   ├── task.py          # Task model (155 lines with Phase 5 fields)
│   │   │   ├── tag.py           # Tag model
│   │   │   └── conversation.py  # Chat models
│   │   ├── services/             # Business logic
│   │   │   ├── tasks.py         # Task service (500+ lines)
│   │   │   ├── chat.py          # Chat processing
│   │   │   ├── events/          # Event publishing
│   │   │   │   ├── publisher.py # Dapr pub/sub client (186 lines)
│   │   │   │   └── schemas.py   # Event data models
│   │   │   └── reminder_scheduler.py  # Background reminder polling (136 lines)
│   │   ├── mcp/                  # Model Context Protocol
│   │   │   ├── agent.py         # Chat agent with 18 tools (400+ lines)
│   │   │   └── tools.py         # MCP tool implementations (500+ lines)
│   │   ├── middleware/           # FastAPI middleware
│   │   │   ├── logging.py       # Structured logging
│   │   │   ├── correlation.py   # Distributed tracing IDs
│   │   │   ├── metrics.py       # Prometheus metrics
│   │   │   └── errors.py        # Global error handling
│   │   ├── utils/                # Utility functions
│   │   │   └── date_parser.py   # Natural language dates
│   │   └── main.py               # Application entry point
│   ├── Dockerfile                # Container image
│   └── pyproject.toml            # Python dependencies
│
├── frontend/                     # Next.js 16 frontend
│   ├── src/
│   │   ├── app/                  # App Router pages
│   │   │   ├── layout.tsx       # Root layout (100 lines)
│   │   │   ├── page.tsx         # Home/landing page
│   │   │   ├── (auth)/          # Auth pages (login, register)
│   │   │   └── home/            # Authenticated home page
│   │   ├── components/           # React components
│   │   │   ├── chat/            # Chat interface components
│   │   │   ├── tasks/           # Task UI components
│   │   │   ├── navigation/      # Headers, sidebars
│   │   │   ├── notifications/   # Notification center
│   │   │   └── ui/              # Shadcn/ui primitives
│   │   ├── lib/                  # Utilities
│   │   │   ├── api.ts           # API client (150+ lines)
│   │   │   └── utils.ts         # Helper functions
│   │   └── types/                # TypeScript types
│   │       ├── task.ts          # Task type definitions
│   │       └── chat.ts          # Chat type definitions
│   ├── public/                   # Static assets
│   ├── Dockerfile                # Container image
│   └── package.json              # Node dependencies
│
├── recurring-service/            # Recurring tasks microservice
│   ├── src/
│   │   ├── api/                  # API endpoints
│   │   │   └── events.py        # Dapr webhook handler
│   │   ├── services/             # Business logic
│   │   │   ├── recurrence.py    # Next occurrence calculator
│   │   │   └── backend_client.py # Backend API client
│   │   ├── handlers/             # Event handlers
│   │   │   └── task_completion_handler.py  # CloudEvent parser (226 lines)
│   │   ├── core/                 # Configuration
│   │   └── main.py               # Service entry point
│   ├── Dockerfile
│   └── pyproject.toml
│
├── notification-service/         # Notification microservice
│   ├── src/
│   │   ├── api/                  # API endpoints
│   │   │   └── reminders.py     # Dapr webhook handler
│   │   ├── services/             # Business logic
│   │   │   └── email_service.py # Resend API integration
│   │   ├── handlers/             # Event handlers
│   │   ├── core/                 # Configuration
│   │   └── main.py               # Service entry point
│   ├── Dockerfile
│   └── pyproject.toml
│
├── helm/                         # Kubernetes deployment
│   └── todo-chatbot/             # Helm chart
│       ├── Chart.yaml            # Chart metadata
│       ├── values.yaml           # Default values
│       ├── helm-values-dapr-enabled.yaml  # Dapr override (242 lines)
│       └── templates/            # K8s manifests
│           ├── backend/          # Backend deployment
│           ├── frontend/         # Frontend deployment
│           ├── recurring-service/ # Recurring service
│           └── notification-service/ # Notification service
│
├── dapr/                         # Dapr configuration
│   ├── components/               # Local Dapr components
│   │   ├── kafka-pubsub.yaml    # Kafka pub/sub component
│   │   └── statestore.yaml      # PostgreSQL state store
│   └── deployment/               # Production Dapr components
│       ├── 01-kafka-pubsub-component.yaml  # Kafka with TLS (93 lines)
│       ├── 02-subscription-task-events.yaml
│       └── 03-subscription-reminders.yaml
│
├── scripts/                      # Deployment automation
│   ├── deploy-all.sh             # Deploy all services (406 lines)
│   ├── deploy-backend.sh         # Deploy backend only
│   ├── deploy-frontend.sh        # Deploy frontend only
│   ├── deploy-recurring-service.sh
│   ├── deploy-notification-service.sh
│   ├── deploy-dapr-enabled.sh    # Dapr-specific deployment
│   └── README.md                 # Scripts documentation (483 lines)
│
├── docker-compose.yml            # Local development setup
├── .env.example                  # Environment template
├── pnpm-workspace.yaml           # pnpm monorepo config
└── README.md                     # This file
```

---

## ⚙️ Configuration

### **Environment Variables**

#### **Backend Configuration**

| Variable                     | Required | Default               | Description                               |
| ---------------------------- | -------- | --------------------- | ----------------------------------------- |
| `DATABASE_URL`               | Yes      | -                     | PostgreSQL connection string              |
| `JWT_SECRET`                 | Yes      | -                     | Secret key for JWT signing (min 32 chars) |
| `JWT_ALGORITHM`              | No       | HS256                 | JWT algorithm                             |
| `JWT_EXPIRATION_HOURS`       | No       | 24                    | Token expiration time                     |
| `CORS_ORIGINS`               | No       | *                     | Comma-separated allowed origins           |
| `OPENAI_API_KEY`             | Yes      | -                     | OpenAI API key for chat                   |
| `OPENAI_MODEL`               | No       | gpt-4.1-2025-04-14    | OpenAI model to use                       |
| `RESEND_API_KEY`             | No       | -                     | Resend API key for emails                 |
| `RESEND_FROM_EMAIL`          | No       | onboarding@resend.dev | Email sender address                      |
| `DAPR_ENABLED`               | No       | true                  | Enable Dapr integration                   |
| `DAPR_HTTP_PORT`             | No       | 3500                  | Dapr sidecar HTTP port                    |
| `PUBSUB_NAME`                | No       | kafka-pubsub          | Dapr pub/sub component name               |
| `REMINDER_POLL_INTERVAL`     | No       | 60                    | Reminder check interval (seconds)         |
| `REMINDER_SCHEDULER_ENABLED` | No       | true                  | Enable reminder scheduler                 |
| `DEBUG`                      | No       | false                 | Enable debug logging                      |

#### **Frontend Configuration**

| Variable                       | Required | Default | Description                           |
| ------------------------------ | -------- | ------- | ------------------------------------- |
| `NEXT_PUBLIC_API_URL`          | No       | ''      | Backend API URL (empty = same domain) |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | No       | -       | Google OAuth client ID (optional)     |

#### **Docker Compose Configuration**

| Variable            | Required | Default | Description         |
| ------------------- | -------- | ------- | ------------------- |
| `POSTGRES_PASSWORD` | Yes      | -       | PostgreSQL password |

### **Dapr Configuration**

**Kafka Pub/Sub Component** (`dapr/deployment/01-kafka-pubsub-component.yaml`):
```yaml
metadata:
  - name: brokers
    secretKeyRef:
      name: kafka-credentials
      key: brokers
  - name: authType
    value: password
  - name: saslMechanism
    value: SCRAM-SHA-512
  - name: tls
    value: "true"
  - name: skipVerify
    value: "true"  # For DigitalOcean Managed Kafka
```

**Subscriptions:**
- `task-events` topic → recurring-service at `/api/events/task`
- `reminders` topic → notification-service at `/api/reminders/handle`

---

## 🔧 Development

### **Backend Development**

```bash
# Navigate to backend
cd backend

# Create virtual environment
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync

# Run development server
fastapi dev src/main.py
```

**Backend Development Tips:**
- Use `/docs` for interactive API testing (Swagger UI)
- Check `logs/` directory for application logs
- Use `pytest` for running tests
- Database migrations with Alembic (if needed)

### **Frontend Development**

```bash
# Navigate to frontend
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

**Frontend Development Tips:**
- Hot reload enabled in dev mode
- Use browser DevTools React extension
- API proxy configured for `/api` routes
- Tailwind CSS IntelliSense extension recommended

### **Microservices Development**

```bash
# Recurring Service
cd recurring-service
uv sync
fastapi dev src/main.py --port 8002

# Notification Service
cd notification-service
uv sync
fastapi dev src/main.py --port 8001
```

### **Local Dapr Development**

```bash
# Initialize Dapr locally
dapr init

# Run backend with Dapr sidecar
dapr run --app-id backend --app-port 8000 --dapr-http-port 3500 \
  --components-path ./dapr/components \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000

# Run recurring service with Dapr
dapr run --app-id recurring-service --app-port 8002 --dapr-http-port 3502 \
  --components-path ./dapr/components \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8002
```

### **Database Management**

```bash
# Connect to local PostgreSQL
docker exec -it phase-5-postgres-1 psql -U postgres -d taskai

# View tables
\dt

# View tasks table schema
\d tasks

# Query tasks
SELECT id, title, priority, due_date, is_completed FROM tasks;

# Backup database
docker exec phase-5-postgres-1 pg_dump -U postgres taskai > backup.sql

# Restore database
docker exec -i phase-5-postgres-1 psql -U postgres taskai < backup.sql
```

---

## 🧪 Testing

### **Backend Tests**

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tasks.py

# Run specific test
pytest tests/test_tasks.py::test_create_task
```

### **Frontend Tests**

```bash
cd frontend

# Run tests (when implemented)
pnpm test

# Run with coverage
pnpm test:coverage

# Run in watch mode
pnpm test:watch
```

### **Integration Tests**

```bash
# Start services
docker-compose up -d

# Run integration tests
cd backend
pytest tests/integration/

# Test API endpoints
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123","full_name":"Test User"}'
```

---

## 🏭 Production

### **Production Deployment (DigitalOcean Kubernetes)**

**Current Production Setup:**
- **Cluster**: do-sgp1-taskai-cluster (Singapore region)
- **Namespace**: todo-app
- **Domain**: https://taskai.asharib.xyz
- **Registry**: registry.digitalocean.com/taskai-registry

**Deployment Status:**
```bash
# Check production pods
kubectl get pods -n todo-app

# Expected output:
# NAME                                                 READY   STATUS
# todo-chatbot-backend-*                               2/2     Running
# todo-chatbot-frontend-*                              1/1     Running
# todo-chatbot-recurring-service-*                     2/2     Running
# todo-chatbot-notification-service-*                  2/2     Running
```

**Verify Dapr Integration:**
```bash
# Check Dapr components
kubectl get component -n todo-app

# Check Dapr subscriptions
kubectl get subscription -n todo-app

# View Dapr sidecar logs
kubectl logs -n todo-app <pod-name> -c daprd
```

**Monitoring:**
```bash
# View application logs
kubectl logs -n todo-app -l app.kubernetes.io/name=backend -c backend --tail=100

# Check resource usage
kubectl top pods -n todo-app

# View events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### **Scaling**

```bash
# Scale backend
kubectl scale deployment todo-chatbot-backend -n todo-app --replicas=5

# Auto-scaling (HPA)
kubectl autoscale deployment todo-chatbot-backend \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n todo-app
```

### **Rollback**

```bash
# View rollout history
kubectl rollout history deployment/todo-chatbot-backend -n todo-app

# Rollback to previous version
kubectl rollout undo deployment/todo-chatbot-backend -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/todo-chatbot-backend -n todo-app --to-revision=2
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### **Development Workflow**

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with clear commit messages
4. **Test your changes**: Run tests and verify locally
5. **Push to your fork**: `git push origin feature/amazing-feature`
6. **Open a Pull Request** with a clear description

### **Commit Message Convention**

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(backend): add task priority filtering
fix(frontend): resolve chat input focus issue
docs(readme): update deployment instructions
chore(deps): update dependencies
```

### **Code Style**

- **Backend**: Follow PEP 8 (use `black` formatter)
- **Frontend**: Follow Airbnb TypeScript style guide (use ESLint)
- Write meaningful variable and function names
- Add comments for complex logic
- Include docstrings for functions

### **Pull Request Checklist**

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New features have tests
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow convention
- [ ] No merge conflicts with main branch

---

## 📄 License

This project is licensed under the [**MIT License**](./LICENSE).

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4.1 API for conversational AI
- **Dapr** - Distributed application runtime
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework for production
- **Vercel** - Shadcn/ui component library
- **DigitalOcean** - Cloud infrastructure
- **PostgreSQL** - Reliable database system
- **Apache Kafka** - Distributed event streaming

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/AsharibAli/Hackathon-II/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AsharibAli/Hackathon-II/discussions)
- **Production Site**: https://taskai.asharib.xyz

---

<p align="center">
  <strong>Built with ❤️ by Asharib Ali</strong>
</p>

<p align="center">
  <sub>TaskAI - Making task management intelligent and effortless</sub>
</p>
