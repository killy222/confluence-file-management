"""
Export a single Confluence page to PDF using the same internal action
as the UI (flyingpdf/pdfpageexport.action).

Usage (env-based):

    CONFLUENCE_URL=https://wiki.viscomp.net \
    CONFLUENCE_USER=user \
    CONFLUENCE_PASSWORD=pass \
    python export_confluence_pdf.py --page-id 139267016 --output-dir ./confluence_export_pdf

This script:
- Calls /spaces/flyingpdf/pdfpageexport.action?pageId={PAGE_ID}
- Follows the redirect Location header to download the generated PDF.
"""

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests


def build_base_url(url: str) -> str:
    url = url.strip()
    if url.endswith("/"):
        url = url[:-1]
    return url


def export_page_pdf(
    base_url: str,
    username: str,
    password: str,
    page_id: str,
    output_dir: Path,
) -> Path:
    base_url = build_base_url(base_url)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({"X-Atlassian-Token": "no-check"})

    export_url = f"{base_url}/spaces/flyingpdf/pdfpageexport.action?pageId={page_id}"
    print(f"Requesting PDF export for page {page_id} at {export_url}...")

    # First request: trigger export, expect redirect
    resp = session.get(export_url, allow_redirects=False)
    if resp.status_code in (301, 302, 303, 307, 308) and "Location" in resp.headers:
        location = resp.headers["Location"]
        if location.startswith("http://") or location.startswith("https://"):
            download_url = location
        else:
            download_url = urljoin(base_url, location)
        print(f"Export redirect to {download_url}")
    elif resp.headers.get("Content-Type", "").startswith("application/pdf"):
        # Some setups may return the PDF directly.
        download_url = None
        pdf_content = resp.content
        print("Received PDF directly from export URL.")
    else:
        print(
            f"Unexpected response from export action: "
            f"status={resp.status_code}, headers={resp.headers}",
            file=sys.stderr,
        )
        resp.raise_for_status()

    if "pdf_content" not in locals():
        # Second request: download the actual PDF file
        dl_resp = session.get(download_url, stream=True)
        dl_resp.raise_for_status()
        pdf_content = dl_resp.content

    out_path = output_dir / f"page_{page_id}.pdf"
    out_path.write_bytes(pdf_content)
    print(f"Saved PDF to {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a Confluence page to PDF using pdfpageexport.action"
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("CONFLUENCE_URL"),
        help="Confluence base URL (or set CONFLUENCE_URL)",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("CONFLUENCE_USER"),
        help="Confluence username (or set CONFLUENCE_USER)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("CONFLUENCE_PASSWORD"),
        help="Confluence password (or set CONFLUENCE_PASSWORD)",
    )
    parser.add_argument(
        "--page-id",
        required=True,
        help="Confluence page ID to export (e.g. 139267016)",
    )
    parser.add_argument(
        "--output-dir",
        default="confluence_export_pdf",
        help="Directory to save the exported PDF (default: confluence_export_pdf)",
    )
    args = parser.parse_args()

    if not args.url or not args.username or not args.password:
        print(
            "Error: CONFLUENCE_URL, CONFLUENCE_USER, and CONFLUENCE_PASSWORD "
            "must be set via env or CLI.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        export_page_pdf(
            base_url=args.url,
            username=args.username,
            password=args.password,
            page_id=str(args.page_id),
            output_dir=Path(args.output_dir),
        )
    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Failed to export PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

