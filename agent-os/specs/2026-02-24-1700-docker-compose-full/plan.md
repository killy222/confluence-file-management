# Phase 4: Docker Compose — Spec and Implementation Plan

## Scope (from roadmap)

- Dockerize backend, frontend, DB, and script runners in separate containers.
- Docker Compose so the full stack runs on another machine with a single `docker compose up`.
- References: Extend existing docker-compose.yml and Dockerfile; reuse backend/frontend layout.

## Target architecture

- **postgres:** Official postgres image; volume; env for user/password/db. Backend connects via DATABASE_URL.
- **backend:** Dockerfile for FastAPI; uvicorn; depends_on postgres; scripts run in same container via subprocess.
- **frontend:** Multi-stage build (Node + nginx); serve dist/ on port 80; VITE_API_URL at build for backend URL.
- **app (optional):** Keep for ad-hoc script runs and tests.

## Tasks

1. Save spec documentation (plan, shape, standards, references, visuals/) — **done**
2. Add postgres service (image, volume, env) — **done**
3. Backend Dockerfile and Compose service (uvicorn, DATABASE_URL, CORS) — **done**
4. Frontend Dockerfile (multi-stage + nginx) and Compose service — **done**
5. Compose integration (depends_on, app optional), .env.example, README — **done**
6. README updates, verify full stack, mark build done — **done**

**Phase 4 build: successfully done.** `docker compose up -d` brings up postgres, backend, frontend; dashboard at http://localhost:80, API at http://localhost:8000.
