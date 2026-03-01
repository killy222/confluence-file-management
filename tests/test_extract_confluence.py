"""Tests for Confluence extraction (label filter, markdown output)."""

import json
import os
import tempfile

import pytest

from extract_confluence import (
    extract_space,
    fetch_page_ids_by_cql,
    page_to_markdown,
    sanitize_filename,
)


def test_sanitize_filename():
    """Sanitize filename keeps safe chars and replaces spaces."""
    assert sanitize_filename("My Page Title") == "My_Page_Title.md"
    assert sanitize_filename("Sales 2024") == "Sales_2024.md"
    assert sanitize_filename("a-b_c") == "a-b_c.md"


def test_page_to_markdown():
    """Page dict is converted to markdown with title and Confluence ID."""
    page = {
        "id": "123",
        "title": "Test Page",
        "body": {"storage": {"value": "<p>Hello <strong>world</strong></p>"}},
    }
    md = page_to_markdown(page)
    assert "# Test Page" in md
    assert "Confluence Page ID: 123" in md
    assert "Hello" in md


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


def test_extract_space_writes_markdown_and_optional_manifest():
    """extract_space writes one markdown file per page and optional manifest."""
    mock_pages = {
        "101": {
            "id": "101",
            "title": "First",
            "body": {"storage": {"value": "<p>Content one</p>"}},
        },
        "102": {
            "id": "102",
            "title": "Second",
            "body": {"storage": {"value": "<p>Content two</p>"}},
        },
    }
    # CQL returns only id/title; get_page_by_id returns full page
    search_results = [{"content": {"id": pid, "title": p["title"]}} for pid, p in mock_pages.items()]

    class MockConfluence:
        def cql(self, cql, start=0, limit=None, expand=None, **kwargs):
            if start == 0:
                return {"results": search_results}
            return {"results": []}

        def get_page_by_id(self, page_id, expand=None, **kwargs):
            return mock_pages.get(str(page_id))

    with tempfile.TemporaryDirectory() as tmp:
        entries = extract_space(
            MockConfluence(),
            "PHONIX",
            "notebook",
            tmp,
            write_manifest=True,
        )

        assert len(entries) == 2
        assert entries[0]["page_id"] == "101"
        assert entries[0]["title"] == "First"
        assert entries[1]["title"] == "Second"

        first_md = os.path.join(tmp, "First.md")
        second_md = os.path.join(tmp, "Second.md")
        assert os.path.isfile(first_md)
        assert os.path.isfile(second_md)
        with open(first_md, encoding="utf-8") as f:
            text = f.read()
        assert "# First" in text
        assert "Confluence Page ID: 101" in text
        assert "Content one" in text

        manifest_path = os.path.join(tmp, "manifest.json")
        assert os.path.isfile(manifest_path)
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        assert len(manifest) == 2
        assert manifest[0]["page_id"] == "101"
        assert manifest[0]["output_path"] == first_md
