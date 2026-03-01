# References for Phase 2 Backend API

## Integration targets (existing scripts)

### extract_confluence.py

- **Location:** project root `extract_confluence.py`
- **Relevance:** Backend will invoke this script for Confluence export. No interface changes; config via env (`CONFLUENCE_URL`, `CONFLUENCE_USER`, `CONFLUENCE_PASSWORD`) and CLI (`--space`, `--label`, `--output-dir`, `--manifest`).
- **Key behavior:** Writes Markdown files to output dir and optional `manifest.json` with `page_id`, `title`, `output_path` per page.

### push_to_notebooklm.py

- **Location:** project root `push_to_notebooklm.py`
- **Relevance:** Backend will invoke this script after export for NotebookLM push. Config via env (`NOTEBOOKLM_HOME` or auth dir, `NOTEBOOKLM_NOTEBOOK_NAME`) and CLI (`--export-dir`, `--notebook`, `--dry-run`).
- **Key behavior:** Reads `manifest.json` from export dir and pushes sources to the given notebook (replace-if-exists by title).

## Product and tech stack

### agent-os/product/tech-stack.md

- **Relevance:** Specifies FastAPI (Python), PostgreSQL, existing Python scripts invoked by backend (subprocess or worker), Python 3.12.
