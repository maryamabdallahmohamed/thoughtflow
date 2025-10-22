# Backend-only Dockerfile for ThoughtFlow Mindmap API
# Builds a minimal image containing only Python runtime and the backend code
# Exposes port 8000 and runs the FastAPI app using Uvicorn

FROM python:3.11-slim

# Set a non-root user
ARG USER=appuser
ARG UID=1000

RUN groupadd -g ${UID} ${USER} \
    && useradd -m -u ${UID} -g ${UID} ${USER} || true

# Set workdir
WORKDIR /app

# Install system deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       git \
    && rm -rf /var/lib/apt/lists/*

# Copy only required files for backend
# Keep the context small by copying manifest and requirements first
COPY requirements.txt ./

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, config, prompts, and main entrypoint
COPY backend/ ./backend/
COPY config/ ./config/
COPY prompts/ ./prompts/
COPY main.py ./

# Create uploads dir and set permissions for runtime
RUN mkdir -p /app/uploads \
    && chown -R ${USER}:${USER} /app/uploads /app

# Drop to non-root user
USER ${USER}

# Expose port used by Uvicorn
EXPOSE 8000

# Default environment variables (can be overridden by docker run -e)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

# Entrypoint: run the FastAPI uvicorn app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
