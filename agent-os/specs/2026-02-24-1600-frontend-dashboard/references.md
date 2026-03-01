# References for Phase 3 Dashboard

## Backend API (data source)

- **Location:** backend/routers/runs.py, files.py, health.py; backend/schemas.py
- **Endpoints:** GET/POST /api/v1/runs, GET /api/v1/runs/{id}, GET /api/v1/files, GET /api/v1/files/by-run/{run_id}, GET /api/v1/health
- **Response types:** RunResponse, ListRunsResponse, ListFilesResponse, ExportedFileResponse, TriggerRunsResponse

## Design reference

- **Visual:** screen.png — Workflow Pro–style dashboard (overview metrics, active pipelines, cloud files). Adapted for Agents: Overview = run metrics; Active Pipelines = run history; Cloud Files = exported files list.
