# Push Confluence to NotebookLM — Shaping Notes

## Scope

- Push script that uploads exported Confluence pages (from manifest + Markdown files) to **one target NotebookLM notebook**.
- **Trigger:** Manual — user runs extract, then runs push when ready.
- **Behavior:** Replace-if-exists by page title so re-runs keep notebook in sync.
- **Tier:** Consumer NotebookLM; use **notebooklm-py** for scripted access.

## Decisions

- **notebooklm-py** for consumer tier (no Enterprise API).
- Config via env or CLI: notebook name/ID, export dir.
- Auth: document notebooklm-py auth (e.g. cookie/token); no secrets in repo.
- Single target notebook; match sources by title for replace-if-exists.

## Context

- **Visuals:** None.
- **References:** extract_confluence.py (output dir, manifest shape); confluence_export/manifest.json and .md files as input.
- **Product alignment:** N/A (no agent-os/product/).

## Standards Applied

- global/coding-style — naming, small functions, DRY.
- global/error-handling — clear messages, fail fast.
- global/conventions — env for config, no secrets.
- testing/test-writing — mock NotebookLM, test behavior.
