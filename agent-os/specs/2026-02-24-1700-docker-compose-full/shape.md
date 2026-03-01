# Phase 4 Docker Compose — Shaping Notes

## Scope

Phase 4 full Docker Compose: separate containers for PostgreSQL, backend API, frontend dashboard, and optional app service for script/tests. Single `docker compose up` runs the stack on any machine.

## Decisions

- Backend and script execution in one container (subprocess); no dedicated worker container.
- Frontend: production build in image; nginx serves static; API URL set at build (e.g. http://backend:8000).
- Secrets via env / .env; no secrets in repo (global/conventions).
- Migrations: one-off command or backend startup.

## Context

- **Visuals:** None.
- **References:** docker-compose.yml, Dockerfile, backend/, frontend/.
- **Product alignment:** roadmap Phase 4, tech-stack (Docker Compose for all services).

## Standards Applied

- global/conventions — env for config, clear docs, project structure.
