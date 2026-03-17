"""
Push Confluence export (manifest + PDF files) to a single NotebookLM notebook.
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
    raise RuntimeError("read_page_content() removed: PDF export uses add_file or PDF→text fallback")


def _read_pdf_text(path: str) -> str:
    """Best-effort PDF text extraction fallback when add_file isn't available."""
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "NotebookLM client does not support PDF upload (add_file missing) and "
            "PDF text extraction fallback requires 'pypdf'. Add it to requirements.txt."
        ) from exc
    reader = PdfReader(path)
    chunks: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            chunks.append(text)
    return "\n\n".join(chunks).strip()


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
        path = resolve_path(export_dir, entry["output_path"])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Export file not found: {path}")
        if not dry_run:
            if hasattr(client.sources, "add_file"):
                try:
                    # notebooklm-py signature: add_file(notebook_id, file_path, mime_type=None, wait=False, ...)
                    await client.sources.add_file(
                        notebook_id,
                        path,
                        mime_type="application/pdf",
                        wait=False,
                    )
                except Exception as exc:
                    msg = str(exc) if exc else ""
                    if "Failed to get SOURCE_ID from registration response" in msg:
                        # Fallback: extract text from PDF and push via add_text so the run still succeeds.
                        content = _read_pdf_text(path)
                        await client.sources.add_text(notebook_id, title, content, wait=False)
                    else:
                        raise
            else:
                content = _read_pdf_text(path)
                await client.sources.add_text(notebook_id, title, content, wait=False)
        added += 1
    return deleted, added


async def truncate_notebook_all(client, notebook_id: str, dry_run: bool = False) -> int:
    """Delete all sources from a NotebookLM notebook by listing and deleting by ID."""
    sources = await client.sources.list(notebook_id)
    if dry_run:
        print(f"[dry-run] Would delete {len(sources)} source(s) from notebook {notebook_id}")
        return len(sources)
    for src in sources:
        await client.sources.delete(notebook_id, src.id)
    return len(sources)


async def run(
    export_dir: str,
    notebook_name_or_id: str,
    dry_run: bool = False,
    truncate_first: bool = True,
    truncate_mode: str = "all",
) -> None:
    """Load manifest, connect to NotebookLM, resolve notebook, optionally truncate, then push."""
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
            if truncate_first:
                if truncate_mode == "all":
                    deleted_total = await truncate_notebook_all(client, notebook_id, dry_run=dry_run)
                    if not dry_run:
                        print(f"Truncated notebook {notebook_id}: deleted {deleted_total} source(s).")
                else:
                    # Placeholder for pipeline-aware truncate using SOURCE_ID tracking
                    print(
                        "[warn] truncate_mode 'pipeline' is not yet implemented; skipping truncation.",
                        file=sys.stderr,
                    )
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
        description="Push Confluence export to a NotebookLM notebook (truncate + replace-if-exists by title)"
    )
    parser.add_argument(
        "--export-dir",
        default=os.environ.get("CONFLUENCE_EXPORT_DIR", "confluence_export_pdf"),
        help="Directory containing manifest.json and .pdf files (default: confluence_export_pdf)",
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
    parser.add_argument(
        "--truncate-first",
        action="store_true",
        default=True,
        help="Delete sources from the target notebook before pushing (default: enabled).",
    )
    parser.add_argument(
        "--truncate-mode",
        choices=["all", "pipeline"],
        default="all",
        help="Truncate mode: 'all' (delete all sources) or 'pipeline' (pipeline-managed sources only; not yet implemented).",
    )
    args = parser.parse_args()

    if not args.notebook:
        print(
            "Error: Notebook name or ID required. Set --notebook or NOTEBOOKLM_NOTEBOOK_NAME / NOTEBOOKLM_NOTEBOOK_ID.",
            file=sys.stderr,
        )
        sys.exit(1)

    asyncio.run(
        run(
            args.export_dir,
            args.notebook,
            dry_run=args.dry_run,
            truncate_first=args.truncate_first,
            truncate_mode=args.truncate_mode,
        )
    )


if __name__ == "__main__":
    main()
