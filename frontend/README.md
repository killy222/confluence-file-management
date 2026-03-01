# Agents Dashboard

Small frontend dashboard for the Agents backend API: run history, exported files, and trigger runs (Confluence export / NotebookLM push).

## Setup

```bash
npm install
```

## Configuration

Set the backend API base URL (default: `http://localhost:8000`):

- Create `.env` with `VITE_API_URL=http://localhost:8000` (or your backend URL)
- Or copy `.env.example` to `.env` and edit

## Run

```bash
npm run dev
```

Open http://localhost:5173. The backend must be running (e.g. `PYTHONPATH=. uvicorn backend.main:app --reload --port 8000`).

## Build

```bash
npm run build
```

Output is in `dist/`. Serve with any static host or point the backend at it for production.
