# References for Push Confluence to NotebookLM

## Similar Implementations

### extract_confluence.py

- **Location:** `extract_confluence.py`
- **Relevance:** Produces the export that the push script consumes. Writes Markdown files and optional manifest.json.
- **Key patterns:** Output dir, manifest shape with `page_id`, `title`, `output_path` (paths may be relative to cwd).

### confluence_export (output)

- **Location:** `confluence_export/manifest.json`, `confluence_export/*.md`
- **Relevance:** Input to push script. manifest.json lists entries with page_id, title, output_path; each output_path points to a .md file with full page content.
- **Key patterns:** Read manifest.json; resolve output_path relative to export dir; read file content for each entry to send as text source to NotebookLM.
