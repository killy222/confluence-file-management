"""
Extract Confluence space pages to PDFs (via Confluence PDF export).
Supports filtering by label (e.g. "notebook") via CQL.
Credentials can be provided via CLI or env: CONFLUENCE_URL, CONFLUENCE_USER, CONFLUENCE_PASSWORD.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
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


def build_base_url(url: str) -> str:
    url = (url or "").strip()
    if url.endswith("/"):
        url = url[:-1]
    return url


def sanitize_filename(title: str, page_id: str) -> str:
    """Build a safe, mostly-human-readable PDF filename from page title + page id."""
    safe = "".join(
        c for c in title if c.isalpha() or c.isdigit() or c in (" ", "-", "_")
    ).strip()
    safe = safe.replace(" ", "_") or "page"
    return f"{safe}_{page_id}.pdf"


def export_page_pdf(
    *,
    base_url: str,
    username: str,
    password: str,
    page_id: str,
    output_path: Path,
) -> Path:
    """
    Export a Confluence page as PDF using the same internal action as the UI:
    /spaces/flyingpdf/pdfpageexport.action?pageId={page_id}
    """
    base_url = build_base_url(base_url)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({"X-Atlassian-Token": "no-check"})

    export_url = f"{base_url}/spaces/flyingpdf/pdfpageexport.action?pageId={page_id}"
    resp = session.get(export_url, allow_redirects=False)
    if resp.status_code in (301, 302, 303, 307, 308) and "Location" in resp.headers:
        location = resp.headers["Location"]
        download_url = (
            location
            if location.startswith("http://") or location.startswith("https://")
            else urljoin(base_url, location)
        )
        dl_resp = session.get(download_url, stream=True)
        dl_resp.raise_for_status()
        pdf_bytes = dl_resp.content
    elif resp.headers.get("Content-Type", "").startswith("application/pdf"):
        pdf_bytes = resp.content
    else:
        resp.raise_for_status()

    output_path.write_bytes(pdf_bytes)
    return output_path


def extract_space(
    confluence,
    base_url: str,
    username: str,
    password: str,
    space_key,
    label,
    output_dir,
    write_manifest=False,
):
    """
    Extract pages from space that have the given label to PDF files.
    Returns list of dicts: [{"page_id", "title", "output_path"}, ...].
    """
    os.makedirs(output_dir, exist_ok=True)
    cql = f'space = "{space_key}" and type = page and label = "{label}"'
    manifest_entries = []

    for page_id, title in fetch_page_ids_by_cql(confluence, cql):
        page_id = str(page_id)
        if not page_id or not title:
            continue
        filename = sanitize_filename(title, page_id)
        filepath = os.path.join(output_dir, filename)

        export_page_pdf(
            base_url=base_url,
            username=username,
            password=password,
            page_id=page_id,
            output_path=Path(filepath),
        )

        manifest_entries.append({"page_id": page_id, "title": title, "output_path": filepath})

    if write_manifest and manifest_entries:
        manifest_path = os.path.join(output_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_entries, f, indent=2)

    return manifest_entries


def main():
    parser = argparse.ArgumentParser(
        description="Extract Confluence space pages to PDFs (optional: by label)"
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
        default="confluence_export_pdf",
        help="Output directory (default: confluence_export_pdf)",
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
        base_url=args.url,
        username=args.username,
        password=args.password,
        space_key=space_key,
        label=args.label,
        output_dir=args.output,
        write_manifest=args.manifest,
    )
    print(f"Done. Extracted {len(entries)} page(s) to {args.output}")


if __name__ == "__main__":
    main()
