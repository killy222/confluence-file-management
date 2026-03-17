"""Tests for Confluence extraction (label filter, PDF output)."""

import json
import os
import tempfile

from extract_confluence import extract_space, fetch_page_ids_by_cql, sanitize_filename


def test_sanitize_filename():
    """Sanitize filename keeps safe chars and replaces spaces."""
    assert sanitize_filename("My Page Title", "123") == "My_Page_Title_123.pdf"
    assert sanitize_filename("Sales 2024", "9") == "Sales_2024_9.pdf"
    assert sanitize_filename("a-b_c", "42") == "a-b_c_42.pdf"


def test_fetch_page_ids_by_cql_calls_cql_with_space_and_label():
    """CQL search is invoked with space and label in the query."""
    seen_cql = []

    def mock_cql(self, cql, start=0, limit=None, expand=None, **kwargs):
        seen_cql.append(cql)
        return {"results": []}

    class MockConfluence:
        cql = mock_cql

    confluence = MockConfluence()
    list(
        fetch_page_ids_by_cql(
            confluence,
            'space = "PHONIX" and type = page and label = "notebook"',
        )
    )
    assert len(seen_cql) == 1
    assert "PHONIX" in seen_cql[0]
    assert "notebook" in seen_cql[0]


def test_extract_space_writes_pdfs_and_optional_manifest(monkeypatch):
    """extract_space writes one PDF file per page and optional manifest."""
    mock_pages = {
        "101": {"id": "101", "title": "First"},
        "102": {"id": "102", "title": "Second"},
    }
    search_results = [
        {"content": {"id": pid, "title": p["title"]}} for pid, p in mock_pages.items()
    ]

    class MockConfluence:
        def cql(self, cql, start=0, limit=None, expand=None, **kwargs):
            if start == 0:
                return {"results": search_results}
            return {"results": []}

    def fake_export_page_pdf(*, base_url, username, password, page_id, output_path):
        assert base_url == "https://wiki.example"
        assert username == "u"
        assert password == "p"
        assert page_id in ("101", "102")
        output_path.write_bytes(b"%PDF-1.4\n%fake\n")
        return output_path

    monkeypatch.setattr("extract_confluence.export_page_pdf", fake_export_page_pdf)

    with tempfile.TemporaryDirectory() as tmp:
        entries = extract_space(
            MockConfluence(),
            base_url="https://wiki.example",
            username="u",
            password="p",
            space_key="PHONIX",
            label="notebook",
            output_dir=tmp,
            write_manifest=True,
        )

        assert len(entries) == 2
        assert {e["page_id"] for e in entries} == {"101", "102"}

        first_pdf = os.path.join(tmp, "First_101.pdf")
        second_pdf = os.path.join(tmp, "Second_102.pdf")
        assert os.path.isfile(first_pdf)
        assert os.path.isfile(second_pdf)
        with open(first_pdf, "rb") as f:
            assert f.read(4) == b"%PDF"

        manifest_path = os.path.join(tmp, "manifest.json")
        assert os.path.isfile(manifest_path)
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        assert len(manifest) == 2
        assert {m["output_path"] for m in manifest} == {first_pdf, second_pdf}
