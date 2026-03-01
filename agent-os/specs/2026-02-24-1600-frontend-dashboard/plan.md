# Phase 3: Frontend Dashboard — Spec and Implementation Plan

**Build: successfully done** (dashboard implemented; design reference: screen.png)

## Scope (from roadmap)

- Small frontend dashboard that consumes the Agents backend API.
- Show: run history (when each operation ran, success/failure), list of exported files.
- Trigger: ability to start runs (Confluence export and/or NotebookLM push) from the dashboard.
- Design reference: Workflow Pro–style layout (dark theme, overview metrics, active pipelines, cloud files).

## Data source (existing API)

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/health` | API status |
| `GET /api/v1/runs` | List runs (paginated; filters: script, status) |
| `GET /api/v1/runs/{id}` | Single run details (log, error_message) |
| `POST /api/v1/runs` | Trigger runs (`{ "scripts": ["confluence_export"] }` or chain) |
| `GET /api/v1/files` | List exported files (optional run_id) |
| `GET /api/v1/files/by-run/{run_id}` | Files for a specific run |

## Tasks

1. Save spec documentation (plan, shape, standards, references, visuals)
2. Frontend project setup (Vite + React, API base URL config)
3. Dashboard UI: overview metrics, run history (Active Pipelines), exported files (Cloud Files), trigger runs
4. API integration and CORS
5. README and mark build done
