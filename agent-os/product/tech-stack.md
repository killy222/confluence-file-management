# Tech Stack

## Backend

- **Framework:** FastAPI (Python).
- **Scripts:** Existing Python (`extract_confluence.py`, `push_to_notebooklm.py`); invoked by backend (subprocess or worker).

## Database

- **Database:** PostgreSQL (run history, file list, config).

## Frontend

- To be chosen in Phase 3 (e.g. React, Vue, or simple HTML/JS).
- Small frontend dashboard that calls the API.

## Runtime and packaging

- **Runtime:** Python 3.12; pip/uv.
- **Containers:** Docker and Docker Compose for all services (API, frontend, DB, script runners) in separate containers.
