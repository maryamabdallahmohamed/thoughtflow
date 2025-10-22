# ThoughtFlow — Backend API (for backend engineer)

This README contains instructions to build and run a backend-only Docker image for the ThoughtFlow Mindmap API and examples for calling the exposed endpoints.

Files included in the image
- `main.py` — FastAPI application entrypoint
- `backend/` — application backend code (loaders, core logic, infrastructure)
- `config/` — runtime settings
- `prompts/` — system prompts used by the LLM services
- `requirements.txt` — Python dependencies

What this image intentionally excludes
- `frontend/` and any frontend assets
- local virtualenvs and development artifacts

Prerequisites
- Docker 20+ installed on the engineer's machine
- (Optional) access/credentials for the LLM provider and embedding service used by `backend.infrastructure` — these are configured via environment variables or mounted secrets as described below.

Build the Docker image

Run from the project root (where this README and `Dockerfile` live):

```bash
docker build -t thoughtflow-backend:latest .
```

Run the container

Basic (development) run, exposing port 8000 and mounting a local `uploads/` directory so files persist:

```bash
mkdir -p uploads
docker run --rm -it \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -e LOG_LEVEL=INFO \
  thoughtflow-backend:latest
```

Notes on environment variables
- `LOG_LEVEL` — sets logging level (DEBUG, INFO, WARNING, ERROR). This is read by `config.settings`.
- LLM / embedder credentials — the project uses `backend.infrastructure.llm` and `backend.infrastructure.embedder`. Provide any required keys via environment variables or mounted secret files. Typical approaches:
  - Pass individual env vars with `-e LLM_API_KEY=...` and `-e EMBEDDER_KEY=...`
  - Or mount a secret/config file at runtime with `-v /path/to/secret:/run/secrets/llm_key:ro` and read it in the app.

Health endpoint
- GET /health — quick check that the service is running and healthy

Upload endpoint
- POST /upload (multipart/form-data) — Uploads a file and returns a JSON object containing `file_path`, `filename`, and `size`.

Example curl for upload (JSON/TXT/PDF supported):

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/document.json"

# Response
# { "file_path": "/app/uploads/1760..._document.json", "filename": "document.json", "size": 12345 }
```

Generate mindmap
- POST /generate_mindmap — JSON body: { "file_path": "/app/uploads/1760..._document.json" }
- Optional fields: `max_depth` (int), `min_size` (int) — will temporarily override runtime clustering settings for that request.

Example curl to generate mindmap:

```bash
curl -X POST "http://localhost:8000/generate_mindmap" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/uploads/1760..._document.json", "max_depth": 4, "min_size": 2}'

# Response: { "mindmap": { ... }, "meta": { "max_depth": 4, "min_size": 2 } }
```

Important operational notes for the backend engineer
- LLM and embedder calls are performed at runtime. They will require network access and valid credentials.
- The code may call external models synchronously, which can be slow — configure timeouts and the environment accordingly.
- The `uploads/` directory is where uploaded files are stored. Mount it to persistent storage when running in production.

Suggested next steps for the engineer
1. Verify/replace the `backend.infrastructure.llm` and `backend.infrastructure.embedder` configurations to use production keys and desired providers.
2. Add secrets management (Docker secrets, environment vars, or a vault) rather than passing keys on the command line.
3. Add a production-ready process manager (systemd, container orchestrator) and configure logging aggregation.
4. Consider adding a lightweight POST /shutdown or admin endpoints (with auth) for controlled shutdowns during maintenance.

Contact
If anything in the API wiring is unclear, inspect `main.py` and `backend/` modules. I included the minimal set of endpoints and file locations in this README.
