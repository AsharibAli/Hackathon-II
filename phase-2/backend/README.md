# Todo Backend API

FastAPI-based REST API for the Todo Full-Stack Web Application.

## Tech Stack

- **Framework:** FastAPI 0.125+
- **ORM:** SQLModel 0.0.14+
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **Migrations:** Alembic
- **Package Manager:** uv

## Project Structure

```
backend/
├── src/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   └── tasks.py      # Task CRUD endpoints
│   ├── core/             # Core utilities
│   │   ├── config.py     # Environment configuration
│   │   ├── database.py   # Database setup
│   │   └── security.py   # JWT & password hashing
│   ├── middleware/       # Custom middleware
│   │   ├── logging.py    # Request logging
│   │   └── errors.py     # Error handling
│   ├── models/           # SQLModel entities
│   │   ├── user.py       # User model
│   │   └── task.py       # Task model
│   ├── services/         # Business logic
│   │   ├── auth.py       # Auth service
│   │   └── tasks.py      # Tasks service
│   └── main.py           # Application entry point
├── alembic/              # Database migrations
├── tests/                # pytest tests
└── pyproject.toml        # Dependencies
```

## Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# JWT Configuration
JWT_SECRET=your-secret-key-here-minimum-32-characters-required
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Application Settings
APP_NAME=Todo Backend API
APP_VERSION=1.0.0
DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Setup

### Prerequisites

- Python 3.11+
- uv package manager: `pip install uv`
- Neon PostgreSQL account: https://neon.tech

### Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### Development

```bash
# Start development server with auto-reload
fastapi dev src/main.py
```

The API will be available at:
- **Base URL:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user (requires auth)

### Tasks

All task endpoints require JWT authentication.

- `GET /api/tasks` - Get all tasks for authenticated user
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{task_id}` - Get specific task
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task
- `PATCH /api/tasks/{task_id}/complete` - Toggle completion status

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Security

- JWT tokens expire after 24 hours (configurable)
- Passwords hashed with bcrypt (cost factor 12)
- Multi-user isolation enforced at service layer
- All task endpoints require authentication
- CORS configured for frontend origin only

## Production Deployment

1. Set `DEBUG=False` in environment variables
2. Use a strong `JWT_SECRET` (min 32 characters)
3. Configure proper `DATABASE_URL` for production database
4. Set appropriate `CORS_ORIGINS`
5. Use a production ASGI server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```
