# References for Phase 4 Docker Compose

## Existing Compose and Dockerfile

- **docker-compose.yml** — Single `app` service; build from root Dockerfile; env for Confluence/NotebookLM; volume mount for auth.
- **Dockerfile** — Python 3.12-slim; scripts + tests; CMD tail -f.

## Backend

- **backend/main.py** — FastAPI app; CORS for localhost:5173.
- **backend/config.py** — database_url (env DATABASE_URL), project_root, export_dir, script paths.
- **backend/runner.py** — execute_runs via subprocess; needs project root and scripts on container filesystem.

## Frontend

- **frontend/** — Vite + React; build to dist/; VITE_API_URL for backend; CORS consumed from backend.
