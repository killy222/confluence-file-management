# Confluence notebook-label extract — Shaping Notes

## Scope

- Extract Confluence pages from a given space that have a specific label (default: `notebook`).
- Output: Markdown files plus optional manifest for a future push step.
- Push to NotebookLM is deferred to a later phase.

## Decisions

- Narrow scope: extract only; no NotebookLM push in this phase.
- Reference implementation: `extract_confluence.py` (space resolution, client, markdownify, file output).
- No visuals.
- Credentials via CLI and/or env (CONFLUENCE_URL, CONFLUENCE_USER, CONFLUENCE_PASSWORD); no secrets in repo.

## Context

- **Visuals:** None.
- **References:** `extract_confluence.py` — space resolution (name vs key), Confluence client, `get_all_pages_from_space`, markdownify, file output and filename sanitization.
- **Product alignment:** N/A (no agent-os/product/ at shape time).

## Standards Applied

- **global/coding-style** — Naming, small functions, DRY.
- **global/error-handling** — Clear messages, fail fast, clean up resources.
- **global/conventions** — Env for config, no secrets in repo.
- **testing/test-writing** — Mock Confluence, test behavior, fast tests.
