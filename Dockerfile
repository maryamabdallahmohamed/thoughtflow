# Backend-only Dockerfile for ThoughtFlow Mindmap API
# Builds a minimal image containing only Python runtime and the backend code
# Exposes port 8000 and runs the FastAPI app using Uvicorn

FROM python:3.12-slim AS builder

# Working directory for build
WORKDIR /app

# Install system dependencies needed for some Python packages (kept minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       git \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage docker cache
COPY requirements.txt ./

# Create a virtualenv and install dependencies in it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY backend/ ./backend/
COPY .env* ./

# Create runtime directories
RUN mkdir -p /app/cache /app/uploads

# Final image: smaller runtime layer
FROM python:3.12-slim

# Create non-root user
ARG APPUSER=appuser
ARG APPUID=1000
RUN groupadd -g ${APPUID} ${APPUSER} \
    && useradd -m -u ${APPUID} -g ${APPUID} ${APPUSER} || true

WORKDIR /app

# Copy venv from builder and set PATH
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy app files from builder
COPY --from=builder /app/backend ./backend



RUN mkdir -p /app/uploads /app/cache \
    && chown -R ${APPUSER}:${APPUSER} /app/uploads /app/cache /app

USER ${APPUSER}


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

# Default command - point to top-level main.py which constructs the app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
