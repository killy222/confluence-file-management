# Push Confluence exports to NotebookLM — Plan

## Scope

- Push script uploads Confluence export (manifest + .md files) to one target NotebookLM notebook.
- Manual trigger; replace-if-exists by title; consumer tier via notebooklm-py.

## Tasks

1. Save spec documentation (plan, shape, standards, references, visuals)
2. Add notebooklm-py and auth documentation
3. Implement push script (read manifest, resolve notebook, list/delete/add sources)
4. Replace-if-exists by title; idempotent re-runs
5. Pytest tests with mocked NotebookLM
6. README and Docker usage for push script

## Spec folder

`agent-os/specs/2026-02-24-1800-push-confluence-to-notebooklm/`
