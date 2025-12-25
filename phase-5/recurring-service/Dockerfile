# [Task]: T099
# [Spec]: F-010 (R-010.6)
# [Description]: Dockerfile for recurring service
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv for faster dependency installation
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system -e .

# Production image
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8002/health')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
