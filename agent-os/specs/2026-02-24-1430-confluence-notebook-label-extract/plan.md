# Plan: Confluence notebook-label extract (extract only)

**Build status:** **Built successfully** (ready)

**Scope:** Add label filter to Confluence extraction so we only export pages from the given space that have the label **notebook**. Push to NotebookLM is deferred to a later phase.

**Spec folder:** `agent-os/specs/2026-02-24-1430-confluence-notebook-label-extract/`

---

## Task 1: Save spec documentation

Create `agent-os/specs/2026-02-24-1430-confluence-notebook-label-extract/` with:

- **plan.md** — This plan (all tasks).
- **shape.md** — Shaping notes: scope (extract only, label filter); decisions (narrow scope, reference extract_confluence.py, no visuals, credentials via env/CLI); context (references = extract_confluence.py; product = N/A; standards = global/coding-style, error-handling, conventions; testing/test-writing).
- **standards.md** — Full content of: global/coding-style.md, global/error-handling.md, global/conventions.md, testing/test-writing.md.
- **references.md** — Pointers to extract_confluence.py: space resolution, Confluence client, get_all_pages_from_space, markdownify, file output and filename sanitization.
- **visuals/** — Empty (no visuals).

---

## Task 2: Add label filter to Confluence extraction

- In **extract_confluence.py** (or a helper it calls), restrict to pages in the resolved space that have the given label (default `notebook`).
- Use **CQL**: `space = "<resolved_space_key>" and label = "notebook"`. Call Confluence REST search or the atlassian client’s CQL/search method. Keep existing space resolution (key first, then search by name).
- Add CLI argument **`--label`** (default `notebook`). Keep existing args: `--url`, `--username`, `--password`, `--space`, `--output`.
- Keep current behaviour: expand `body.storage`, convert HTML to Markdown (markdownify), one `.md` file per page, include Confluence Page ID in header.
- Optional: write a **manifest** (e.g. JSON) under the output dir with page_id, title, output_path for a future push step.
- Use env for credentials where possible (e.g. CONFLUENCE_URL, CONFLUENCE_USER, CONFLUENCE_PASSWORD) and document in README; no secrets in repo.

---

## Task 3: Add tests

- **pytest** tests with mocked Confluence:
  - CQL/search is called with space + label (e.g. label=notebook and correct space key).
  - Given a mock response with 1–2 pages, the script (or extracted function) produces expected Markdown output and filenames (or manifest if implemented).
- Tests fast and behavior-focused; mock external Confluence (per test-writing standard).

---

## Task 4: Document env and usage

- **README** (or equivalent): how to run the script (CLI and env for URL/user/password). Document `--label` and default `notebook`. Note that this phase is extract-only; push to NotebookLM is planned later.

---

## Summary

| Task | Action |
|------|--------|
| 1 | Create spec folder and add plan.md, shape.md, standards.md, references.md, visuals/ |
| 2 | Add CQL/label filter and --label to extract_confluence.py |
| 3 | Add pytest tests for label filter and output |
| 4 | Document env and usage in README |
