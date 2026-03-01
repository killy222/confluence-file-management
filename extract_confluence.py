"""
Extract Confluence space pages to Markdown.
Supports filtering by label (e.g. "notebook") via CQL.
Credentials can be provided via CLI or env: CONFLUENCE_URL, CONFLUENCE_USER, CONFLUENCE_PASSWORD.
"""

import argparse
import json
import os
import sys

import markdownify
from atlassian import Confluence


def resolve_space_key(confluence, space_key_or_name):
    """Resolve space key from key or name. Returns key or raises ValueError."""
    try:
        space = confluence.get_space(space_key_or_name)
        return space["key"]
    except Exception:
        results = confluence.get_all_spaces(
            start=0, limit=50, expand="description.plain,homepage"
        )
        for s in results["results"]:
            if (
                s["name"].lower() == space_key_or_name.lower()
                or s["key"].lower() == space_key_or_name.lower()
            ):
                return s["key"]
        raise ValueError(f"Could not find space '{space_key_or_name}'")


def fetch_page_ids_by_cql(confluence, cql, limit=50):
    """Yield (page_id, title) from Confluence CQL search. No body expand - search does not return full body."""
    start = 0
    while True:
        response = confluence.cql(cql, start=start, limit=limit, expand=None)
        if not response:
            break
        results = response.get("results") or []
        for item in results:
            content = item.get("content", item)
            yield content.get("id"), content.get("title")
        if len(results) < limit:
            break
        start += limit


def get_full_page(confluence, page_id):
    """Fetch a single page by ID with full body storage (for complete content)."""
    return confluence.get_page_by_id(page_id, expand="body.storage")


def page_to_markdown(page):
    """Convert a Confluence page dict to markdown string."""
    title = page["title"]
    body_html = page.get("body", {}).get("storage", {}).get("value", "")
    markdown_text = markdownify.markdownify(body_html, heading_style="ATX")
    return f"# {title}\n\nConfluence Page ID: {page['id']}\n\n{markdown_text}"


def sanitize_filename(title):
    """Build a safe filename from page title."""
    safe = "".join(
        c for c in title if c.isalpha() or c.isdigit() or c in (" ", "-", "_")
    ).strip()
    return safe.replace(" ", "_") + ".md"


def extract_space(
    confluence,
    space_key,
    label,
    output_dir,
    write_manifest=False,
):
    """
    Extract pages from space that have the given label to Markdown files.
    Returns list of dicts: [{"page_id", "title", "output_path"}, ...].
    """
    os.makedirs(output_dir, exist_ok=True)
    cql = f'space = "{space_key}" and type = page and label = "{label}"'
    manifest_entries = []

    for page_id, title in fetch_page_ids_by_cql(confluence, cql):
        # CQL search does not return full body; fetch full page by ID
        page = get_full_page(confluence, page_id)
        if not page:
            continue
        filename = sanitize_filename(title)
        filepath = os.path.join(output_dir, filename)

        content = page_to_markdown(page)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        manifest_entries.append(
            {"page_id": page["id"], "title": title, "output_path": filepath}
        )

    if write_manifest and manifest_entries:
        manifest_path = os.path.join(output_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_entries, f, indent=2)

    return manifest_entries


def main():
    parser = argparse.ArgumentParser(
        description="Extract Confluence space to Markdown (optional: by label)"
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("CONFLUENCE_URL"),
        help="Confluence URL (or set CONFLUENCE_URL)",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("CONFLUENCE_USER"),
        help="Username (or set CONFLUENCE_USER)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("CONFLUENCE_PASSWORD"),
        help="Password (or set CONFLUENCE_PASSWORD)",
    )
    parser.add_argument("--space", required=True, help="Space Key or Name to extract")
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory",
    )
    parser.add_argument(
        "--label",
        default="notebook",
        help="Only export pages with this label (default: notebook)",
    )
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Write manifest.json with page_id, title, output_path",
    )
    args = parser.parse_args()

    if not args.url or not args.username or not args.password:
        print(
            "Error: Confluence URL, username and password are required. "
            "Set CONFLUENCE_URL, CONFLUENCE_USER, CONFLUENCE_PASSWORD or pass --url, --username, --password.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Connecting to {args.url} as {args.username}...")
    try:
        confluence = Confluence(
            url=args.url,
            username=args.username,
            password=args.password,
            verify_ssl=False,
        )
        confluence.get_user_details_by_username(args.username)
    except Exception as e:
        print(f"Failed to connect: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        space_key = resolve_space_key(confluence, args.space)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print(f"Fetching pages from space {space_key} with label '{args.label}'...")
    entries = extract_space(
        confluence,
        space_key,
        args.label,
        args.output,
        write_manifest=args.manifest,
    )
    print(f"Done. Extracted {len(entries)} page(s) to {args.output}")


if __name__ == "__main__":
    main()
