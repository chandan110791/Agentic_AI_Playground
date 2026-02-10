# Multi-stage Dockerfile optimized for UV and Google ADK
# This builds a production-ready container with minimal size and secure defaults

# --- Build Stage ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml .python-version ./

# Install dependencies to a specific location
RUN uv sync --frozen --no-dev --no-install-project

# --- Final Stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy the non-root user from builder
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group

# Copy installed dependencies
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run the production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

