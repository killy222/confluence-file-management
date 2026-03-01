"""
Push Confluence export (manifest + Markdown files) to a single NotebookLM notebook.
Replace-if-exists: sources with the same title are deleted then re-added with current content.
Requires notebooklm-py and one-time auth: run `notebooklm login`.
"""

import argparse
import asyncio
import json
import os
import sys


def load_manifest(export_dir: str) -> list[dict]:
    """Load manifest.json from export dir. Raises FileNotFoundError if missing."""
    path = os.path.join(export_dir, "manifest.json")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Manifest not found: {path}. Run extract with --manifest first.")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("manifest.json must be a list of {page_id, title, output_path}")
    return data


def resolve_path(export_dir: str, output_path: str) -> str:
    """Resolve output_path (may be relative) against export_dir."""
    if os.path.isabs(output_path):
        return output_path
    return os.path.normpath(os.path.join(export_dir, os.path.basename(output_path)))


def read_page_content(export_dir: str, entry: dict) -> str:
    """Read Markdown content for one manifest entry."""
    path = resolve_path(export_dir, entry["output_path"])
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Export file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return f.read()


async def resolve_notebook_id(client, notebook_name_or_id: str) -> str:
    """Resolve notebook by ID (if long enough) or by title. Returns notebook id."""
    notebook_name_or_id = (notebook_name_or_id or "").strip()
    if not notebook_name_or_id:
        raise ValueError("Notebook name or ID is required")
    # If it looks like an ID (long string), try use as-is; else find by title
    if len(notebook_name_or_id) >= 20 and "/" not in notebook_name_or_id:
        return notebook_name_or_id
    notebooks = await client.notebooks.list()
    for nb in notebooks:
        if nb.title and nb.title.strip().lower() == notebook_name_or_id.lower():
            return nb.id
        if nb.id == notebook_name_or_id:
            return nb.id
    raise ValueError(
        f"No notebook found with name or ID '{notebook_name_or_id}'. "
        "Create it in NotebookLM or pass the notebook ID."
    )


async def push_export(
    client,
    notebook_id: str,
    entries: list[dict],
    export_dir: str,
    dry_run: bool = False,
) -> tuple[int, int]:
    """
    For each manifest entry: delete existing source with same title if any, then add source.
    Returns (deleted_count, added_count).
    """
    sources = await client.sources.list(notebook_id)
    by_title = { (s.title or "").strip(): s for s in sources if s.title }

    deleted = 0
    added = 0
    for entry in entries:
        title = (entry.get("title") or "").strip()
        if not title:
            continue
        existing = by_title.get(title)
        if existing:
            if not dry_run:
                await client.sources.delete(notebook_id, existing.id)
            deleted += 1
            del by_title[title]
        content = read_page_content(export_dir, entry)
        if not dry_run:
            await client.sources.add_text(notebook_id, title, content, wait=False)
        added += 1
    return deleted, added


async def run(
    export_dir: str,
    notebook_name_or_id: str,
    dry_run: bool = False,
) -> None:
    """Load manifest, connect to NotebookLM, resolve notebook, push with replace-if-exists."""
    from notebooklm import NotebookLMClient

    export_dir = os.path.abspath(export_dir)
    if not os.path.isdir(export_dir):
        print(f"Error: Export directory not found: {export_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        entries = load_manifest(export_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("No entries in manifest. Nothing to push.")
        return

    try:
        async with await NotebookLMClient.from_storage() as client:
            notebook_id = await resolve_notebook_id(client, notebook_name_or_id)
            if dry_run:
                print(f"[dry-run] Would push {len(entries)} source(s) to notebook {notebook_id}")
            deleted, added = await push_export(client, notebook_id, entries, export_dir, dry_run=dry_run)
            if dry_run:
                print(f"[dry-run] Would delete {deleted} existing, add {added} new")
            else:
                print(f"Done. Deleted {deleted} existing source(s), added {added} new.")
    except FileNotFoundError as e:
        if "storage_state" in str(e) or "Storage file" in str(e):
            print(
                "Error: NotebookLM auth not found. Run 'notebooklm login' once to authenticate.",
                file=sys.stderr,
            )
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push Confluence export to a NotebookLM notebook (replace-if-exists by title)"
    )
    parser.add_argument(
        "--export-dir",
        default=os.environ.get("CONFLUENCE_EXPORT_DIR", "confluence_export"),
        help="Directory containing manifest.json and .md files (default: confluence_export)",
    )
    parser.add_argument(
        "--notebook",
        default=os.environ.get("NOTEBOOKLM_NOTEBOOK_NAME") or os.environ.get("NOTEBOOKLM_NOTEBOOK_ID"),
        help="Notebook name or ID (or set NOTEBOOKLM_NOTEBOOK_NAME / NOTEBOOKLM_NOTEBOOK_ID)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would be done without calling delete/add",
    )
    args = parser.parse_args()

    if not args.notebook:
        print(
            "Error: Notebook name or ID required. Set --notebook or NOTEBOOKLM_NOTEBOOK_NAME / NOTEBOOKLM_NOTEBOOK_ID.",
            file=sys.stderr,
        )
        sys.exit(1)

    asyncio.run(run(args.export_dir, args.notebook, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
