# Confluence to Markdown extractor

Extract Confluence space pages to Markdown files, with optional filtering by label (e.g. `notebook`). Useful for syncing wiki content to other systems (e.g. NotebookLM) in a later phase.

## Requirements

- Python 3.10+
- Dependencies: `pip install -r requirements.txt`

## Configuration

Credentials can be set via **environment variables** (recommended) or CLI arguments. Do not commit secrets to version control.

| Variable             | Description        |
|----------------------|--------------------|
| `CONFLUENCE_URL`     | Confluence base URL (e.g. `https://wiki.example.com`) |
| `CONFLUENCE_USER`    | Username           |
| `CONFLUENCE_PASSWORD`| Password           |

## Usage

```bash
# Using env vars
export CONFLUENCE_URL=https://wiki.viscomp.net
export CONFLUENCE_USER=your_user
export CONFLUENCE_PASSWORD=your_pass
python extract_confluence.py --space "Phonix Sales" --output ./output

# Override via CLI
python extract_confluence.py --url https://wiki.viscomp.net --username user --password pass \
  --space "Phonix Sales" --output ./output
```

### Options

| Option       | Default | Description |
|-------------|---------|-------------|
| `--url`     | `CONFLUENCE_URL` | Confluence base URL |
| `--username`| `CONFLUENCE_USER`| Username |
| `--password`| `CONFLUENCE_PASSWORD` | Password |
| `--space`   | *(required)* | Space key or space name (e.g. `Phonix Sales`) |
| `--output`  | `output` | Directory to write Markdown files |
| `--label`   | `notebook` | Only export pages that have this label |
| `--manifest`| off | Write `manifest.json` in the output dir with `page_id`, `title`, `output_path` (for later push steps) |

### Examples

```bash
# Extract only pages tagged "notebook" from space "Phonix Sales" (default label)
python extract_confluence.py --space "Phonix Sales" --output ./notebooks

# Use a different label and write manifest for downstream sync
python extract_confluence.py --space "Phonix Sales" --label "export" --output ./out --manifest
```

## Push to NotebookLM

After extracting (with `--manifest`), you can push the export to a single **NotebookLM** notebook. Sources are matched by **title**; if a source with the same title already exists, it is deleted and re-added with the current content (replace-if-exists).

### Auth (one-time, optional)

NotebookLM uses **browser-based login** only (no email/password in the script). You have two options:

- **Option A — Host login (CLI / scripts):**  
  Run once on your machine:

  ```bash
  pip install "notebooklm-py[browser]"   # if you need browser login
  notebooklm login                       # opens browser; sign in with your Google account; credentials saved to ~/.notebooklm/
  ```

  After that, the push script can run without interaction. Do not commit `~/.notebooklm/` or any auth files.

- **Option B — Upload auth file in the dashboard (recommended for Docker users):**  
  On a machine where you have already logged in with `notebooklm login`, locate the `storage_state.json` file:

  - Linux/macOS: `~/.notebooklm/storage_state.json`
  - Windows: `%USERPROFILE%\.notebooklm\storage_state.json`

  Then open the dashboard (http://localhost:80) and use the **“Upload NotebookLM auth”** button to upload that file. The backend stores it under `NOTEBOOKLM_HOME/storage_state.json` so all push operations use it. Never share this file or commit it to git.

### Env and CLI

| Variable | Description |
|----------|-------------|
| `NOTEBOOKLM_NOTEBOOK_NAME` or `NOTEBOOKLM_NOTEBOOK_ID` | Target notebook name or ID (or use `--notebook`) |
| `CONFLUENCE_EXPORT_DIR` | Export directory (default: `confluence_export`); can override with `--export-dir` |

```bash
# Push to a notebook by name (must exist in your NotebookLM)
python push_to_notebooklm.py --export-dir ./confluence_export --notebook "Phonix Sales"

# Or set env and run
export NOTEBOOKLM_NOTEBOOK_NAME="Phonix Sales"
python push_to_notebooklm.py

# Dry run (no delete/add)
python push_to_notebooklm.py --notebook "Phonix Sales" --dry-run
```

The export directory must contain `manifest.json` (from `extract_confluence.py --manifest`) and the referenced `.md` files.

## Current scope

Extract: Confluence space + label to Markdown and optional manifest. Push: one target NotebookLM notebook with replace-if-exists by title.

## Docker

**Windows users:** See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for a full installation and run guide (prerequisites, Docker, and optional NotebookLM auth).

### Phase 4: Full stack with Docker Compose

Run the full stack (PostgreSQL, backend API, frontend dashboard) in separate containers:

```bash
# Copy env example and set POSTGRES_PASSWORD etc. if desired
cp .env.example .env

# Build and start postgres, backend, frontend
docker compose up -d --build

# Run migrations (one-off; run from backend dir in container)
docker compose run --rm -w /app/backend backend python -m alembic upgrade head
```

- **Frontend (dashboard):** http://localhost:80
- **Backend API / docs:** http://localhost:8000 and http://localhost:8000/docs
- **PostgreSQL:** localhost:5432 (user/password/db from `.env` or defaults in [docker-compose.yml](docker-compose.yml))

To run scripts or tests in a container, use the **app** service (profile `tools`):

```bash
# Run tests
docker compose --profile tools run --rm app pytest tests/ -v

# Run extract (set CONFLUENCE_* in .env or pass env)
docker compose --profile tools run --rm app python extract_confluence.py --space PHS --label notebook --output /app/confluence_export --manifest

# Run push (NotebookLM auth managed inside the backend container)
docker compose --profile tools run --rm app python push_to_notebooklm.py --export-dir ./confluence_export --notebook "Phonix Sales"

# Shell
docker compose --profile tools run --rm app bash
```

Confluence and NotebookLM credentials: set in `.env` or pass when running. The backend and app containers use an internal `/app/.notebooklm` directory for NotebookLM auth (`NOTEBOOKLM_HOME=/app/.notebooklm`). You can upload `storage_state.json` via the dashboard; it is stored only inside the container and no longer mounted from the host.

## Backend API (Phase 2)

FastAPI backend to trigger Confluence export and NotebookLM push scripts and persist run history.

### Run locally

1. **PostgreSQL** must be running (e.g. local or Docker).
2. Set `DATABASE_URL` (optional; default `postgresql+asyncpg://postgres:postgres@localhost:5432/agents`).
3. From project root:

```bash
pip install -r backend/requirements.txt
PYTHONPATH=. uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- API base: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `GET /api/v1/health`

### Migrations

From project root (PostgreSQL must be running):

```bash
cd backend && PYTHONPATH=.. alembic upgrade head
```

To roll back: `alembic downgrade -1`.

### Env vars (backend)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL URL with async driver, e.g. `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `PROJECT_ROOT` | Optional; project root path (default: parent of `backend/`) |
| `CONFLUENCE_URL`, `CONFLUENCE_USER`, `CONFLUENCE_PASSWORD` | Passed through to extract script when triggering runs |
| `NOTEBOOKLM_NOTEBOOK_NAME`, `CONFLUENCE_EXPORT_DIR` | Passed through to push script |

### Confluence spaces configuration

Confluence spaces are now managed from the **dashboard**:

- Use the **“Confluence spaces”** panel (left column, under Active pipelines) to:
  - Add spaces by **label** (e.g. `Phonix Sales`) and **space key** (e.g. `PHS`).
  - Edit labels or delete spaces.
- The **Run Confluence Export** / **Run all** buttons use the space selected in the **Confluence space** dropdown.
  - The backend looks up the space by ID and stores its `space_key` on each `confluence_export` run.
  - The most recently used space is reused as the default when possible.

You can still set `CONFLUENCE_SPACE` in `.env` as a legacy default, but the recommended flow is to manage spaces via the dashboard selector.

### NotebookLM notebooks configuration

NotebookLM notebooks are also managed from the **dashboard**:

- Use the **“NotebookLM notebooks”** section (left column, below Confluence spaces) to:
  - Add notebook names that correspond to your NotebookLM notebooks (e.g. `Phonix Sales`).
  - Edit or delete notebook targets as needed.
- The **Run push files to notebook** / **Run all** buttons use the notebook selected in the **NotebookLM notebook** dropdown.
  - The backend resolves the selected notebook at trigger-time and stores the `notebook_name` on each `notebooklm_push` run.
  - The most recently used notebook is reused as the default when possible.

`NOTEBOOKLM_NOTEBOOK_NAME` in `.env` remains a legacy fallback only; normal operation should use the dashboard-managed notebook selector.

### Truncate NotebookLM notebook before push (optional)

By default, pushes use a **replace-by-title** strategy only: per page, existing sources with the same title are deleted and re-added.

You can instead choose to **clear the entire target NotebookLM notebook before each push**:

- Set `NOTEBOOKLM_TRUNCATE_BEFORE_PUSH=true` in `.env` (or the backend environment).
- When this is enabled, the backend will call `push_to_notebooklm.py` with `--truncate-first`, which:
  - Lists all sources in the selected notebook.
  - Deletes them by ID.
  - Then pushes the current PDFs.

Use this only for notebooks dedicated to this pipeline, since it will remove any manually added sources as well.

## Dashboard (Phase 3)

React dashboard (Vite + Tailwind) that consumes the backend API: run history, exported files list, and trigger runs.

```bash
cd frontend && npm install && npm run dev
```

Set `VITE_API_URL` (default `http://localhost:8000`) if the backend runs elsewhere. CORS is enabled for `http://localhost:5173` and `http://127.0.0.1:5173`. See [frontend/README.md](frontend/README.md).

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

### Backend API tests

```bash
pip install -r backend/requirements.txt
cd backend && PYTHONPATH=.. pytest tests/ -v
```

- **Schema tests** (no DB): always run.
- **API tests** (runs, files, health): require `DATABASE_URL` (PostgreSQL). If unset, they are skipped. The script runner is mocked so no real subprocess runs.
