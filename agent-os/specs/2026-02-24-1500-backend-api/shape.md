# Phase 2 Backend API — Shaping Notes

## Scope

Phase 2 Backend API: FastAPI + PostgreSQL to trigger Confluence export and NotebookLM push scripts separately or in chain, with persisted run history and exported file list.

## Decisions

- **Subprocess invocation:** Backend invokes existing `extract_confluence.py` and `push_to_notebooklm.py` via subprocess (or asyncio subprocess). No changes to script interfaces; config via env and CLI args.
- **Persist after run:** Run history and file list are written by the backend after each run (parsing script output or reading export dir/manifest).
- **API versioning:** Optional version prefix (e.g. `/api/v1`) per backend/api standard.
- **Async runs:** POST /runs returns 202 with run id(s); scripts run asynchronously (background task or worker).

## Context

- **Visuals:** None.
- **References:** No existing codebase references provided; existing scripts are integration targets only.
- **Product alignment:** Aligns with [agent-os/product/roadmap.md](../../product/roadmap.md) Phase 2 (Backend API) and [agent-os/product/tech-stack.md](../../product/tech-stack.md) (FastAPI, PostgreSQL).

## Standards Applied

- **backend/api** — RESTful design, plural nouns, versioning, HTTP status codes (200, 201, 202, 400, 404, 500).
- **backend/models** — Timestamps, constraints, indexes on FKs, clear naming.
- **backend/migrations** — Reversible migrations, small focused changes, clear naming.
- **global/error-handling** — Centralized error handling, clear messages, fail fast.
