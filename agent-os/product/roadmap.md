# Product Roadmap

## Phase 1: MVP

- Confluence extract by space + label; push to NotebookLM (one notebook, replace-if-exists).
- Run scripts separately or in chain: after Confluence export finishes, start NotebookLM push.

## Phase 2: Post-MVP — Backend API

- FastAPI backend + PostgreSQL.
- Manage scripts: trigger Confluence export and/or NotebookLM push separately or in chain.
- Persist: list of files downloaded/exported, run history (when each operation ran, success/failure).

## Phase 3: Post-MVP — Dashboard

- Small frontend dashboard that consumes the API.
- Show run history, success/failure, and list of exported/files (and any other info the API exposes).

## Phase 4: Post-MVP — Docker Compose

- Dockerize backend, frontend, DB, and script runners in separate containers.
- Docker Compose so everything can run on another machine.
