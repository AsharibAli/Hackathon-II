FROM python:3.11-slim

WORKDIR /app

# Install uv for fast package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
# Disable uv cache (not needed in container)
ENV UV_NO_CACHE=1

# Step 1: Copy ONLY dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Step 2: Install dependencies (this layer is cached unless deps change)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Step 3: Copy source code AFTER deps installed (code changes don't bust dep cache)
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Step 4: Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Set working directory to src for correct imports
WORKDIR /app/src

# Run the app
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
