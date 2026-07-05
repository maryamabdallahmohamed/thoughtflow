# ThoughtFlow — Backend API (for backend & frontend development)

This README explains how to build and run the backend Docker image, how to call the API endpoints, and how to integrate the API from a separately hosted frontend. Note: the image does NOT contain or serve any frontend assets — the backend runs independently and has no access to your frontend bundle.

Quick overview
- Image contains:  `backend/`
- Network: container exposes port `8000`. Frontend must call the backend over HTTP(S) using the container/host address.


Run the container (dev example)
Mount `uploads/` so files persist and expose port 8000:


```env
# .env (example)
DEVICE=
CACHE_DIR="cache/"
Groq_API=
DATABASE_URL=
```

- Preferred ways to provide secrets/config:
  - For development with Docker: use --env-file to pass the `.env` into the running container:
    ```bash
    docker run --rm -it \
      -p 8000:8000 \
      -v $(pwd)/uploads:/app/uploads \
      --env-file .env \
      thoughtflow-backend:latest
    ```
  - For production: use Docker secrets / cloud secret manager / environment injection in your orchestrator (avoid baking secrets into the image).
  - Note: the project's Dockerfile copies `.env*` at build time if present, but copying secrets into images is discouraged. Prefer runtime injection (`--env-file` or secrets).

Health & docs
- GET /health — health check
- Open API docs: GET /docs (when container is reachable)

Endpoints — usage and examples
1) Upload a document (JSON/PDF/TXT)
- Frontend should POST multipart/form-data to /upload. The response includes `file_path` which is an absolute path inside the container — pass that path to /generate_mindmap.

Example curl:

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/document.json"

# Response
# { "file_path": "/app/uploads/1760..._document.json", "filename": "document.json", "size": 12345 }
```

2) Generate mindmap
- POST JSON to /generate_mindmap with `file_path` returned by /upload. Optional fields: `max_depth`, `min_size` to temporarily override clustering settings for that request.

Example curl:

```bash
curl -X POST "http://localhost:8000/generate_mindmap" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/uploads/1760..._document.json", "max_depth": 4, "min_size": 2"}'
# Response: { "mindmap": { ... }, "meta": { "max_depth": 4, "min_size": 2 } }
```

Frontend integration notes
- The backend image will not serve your frontend. Host the frontend separately (Vite dev server, static hosting, or CDN) and configure it to call the backend URL (e.g., http://localhost:8000 or your production API host).
- CORS: the backend currently uses CORSMiddleware allowing "*" — acceptable for local dev but tighten to your frontend origin in production.
- Workflow from frontend:
  1. Upload file via POST /upload (multipart/form-data) → receive `file_path`.
  2. POST to /generate_mindmap with the returned `file_path` → receive mindmap JSON.
  3. Render the returned `mindmap` tree in the frontend.

Example minimal frontend fetch (in a Vite/React app, set API base in env var):

```javascript
// example: src/api.ts
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: form });
  return res.json(); // { file_path, filename, size }
}

export async function generateMindmap(filePath, opts = {}) {
  const body = JSON.stringify({ file_path: filePath, ...opts });
  const res = await fetch(`${API_BASE}/generate_mindmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  return res.json(); // { mindmap, meta }
}
```

Tips for frontend development
- Do not rely on container internal paths for long-term storage. If you need to persist beyond the container, store uploaded files in a shared volume, S3, or another external store and pass a stable reference to the backend (you can modify the backend to accept external URLs if needed).
- Be prepared for long-running requests: generating a mindmap can make external LLM calls and take time. Consider:
  - Showing progress UI / spinner.
  - Using a server-side task queue (Celery/RQ) and a status endpoint for async processing if you need non-blocking behavior.
  - Increasing client and proxy timeouts.

Configurable parameters
- Temporary runtime overrides can be sent in /generate_mindmap: `max_depth`, `min_size`.
- Embedding batch size and defaults come from `config/settings`. To change defaults, modify config or expose env vars via the container.

Security & production checklist
- Narrow CORS allowlist to trusted frontend origin(s).
- Serve backend over HTTPS and enforce auth (API keys, OAuth, JWT) for production.
- Use secure secret management for LLM/embedder keys (Docker secrets, Vault, or cloud secret manager).
- Add rate limiting, authentication, input validation, and monitoring/log aggregation.
- Run container behind a reverse proxy and configure graceful shutdown / health checks.

Troubleshooting
- 404 from /generate_mindmap: ensure you passed the `file_path` returned by /upload and that the uploads volume is mounted in the container you call.
- Long runtimes / timeouts: monitor logs, consider async task processing.
- Missing credentials / 5xx: verify env vars for LLM/embedder are present inside the container.
``
