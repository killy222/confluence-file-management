# References for Confluence notebook-label extract

## Similar Implementations

### extract_confluence.py

- **Location:** `extract_confluence.py` (project root)
- **Relevance:** Current Confluence extraction script; base for adding label filter and CQL.
- **Key patterns:**
  - Space resolution: try space by key first, then search `get_all_spaces` by name/key.
  - Confluence client: `Confluence(url, username, password, verify_ssl=False)`.
  - Page fetch: `get_all_pages_from_space(space_key, start, limit, expand='body.storage')`.
  - HTML to Markdown: `markdownify.markdownify(body_html, heading_style="ATX")`.
  - File output: sanitize title to filename (alphanumeric, space, hyphen, underscore), write `# {title}\n\nConfluence Page ID: {id}\n\n{markdown}`.
  - Error handling: connection and space-not-found exit with clear messages.
