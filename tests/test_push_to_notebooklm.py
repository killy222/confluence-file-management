"""Tests for push_to_notebooklm (replace-if-exists, add-only)."""

import asyncio
import json
import os
import tempfile

import pytest

from push_to_notebooklm import load_manifest, push_export, read_page_content, resolve_path


def test_load_manifest_missing_raises():
    """Missing manifest.json raises FileNotFoundError."""
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            load_manifest(tmp)


def test_load_manifest_valid_returns_entries():
    """Valid manifest.json returns list of entries."""
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = os.path.join(tmp, "manifest.json")
        data = [
            {"page_id": "1", "title": "One", "output_path": "One.md"},
        ]
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        assert load_manifest(tmp) == data


def test_resolve_path_relative():
    """output_path is resolved as export_dir + basename (manifest paths are under export_dir)."""
    assert resolve_path("/app/export", "Page.md") == os.path.normpath("/app/export/Page.md")
    assert resolve_path("/app/export", "./confluence_export/Page.md").endswith("Page.md")


def test_read_page_content():
    """read_page_content returns file content for manifest entry."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "Doc.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Doc\n\nHello.")
        entry = {"title": "Doc", "output_path": "Doc.md"}
        assert read_page_content(tmp, entry) == "# Doc\n\nHello."


def test_push_export_add_only_when_no_existing_sources():
    """When notebook has no sources, only add_text is called (no delete)."""
    deleted_calls = []
    added_calls = []

    class MockClient:
        class Sources:
            async def list(self, notebook_id):
                return []

            async def delete(self, notebook_id, source_id):
                deleted_calls.append((notebook_id, source_id))

            async def add_text(self, notebook_id, title, content, wait=False):
                added_calls.append((notebook_id, title, content))

        sources = Sources()

    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "A.md"), "w", encoding="utf-8") as f:
                f.write("# A\n\nContent A")
            entries = [{"page_id": "1", "title": "A", "output_path": "A.md"}]
            client = MockClient()
            return await push_export(client, "nb1", entries, tmp, dry_run=False), deleted_calls, added_calls

    (deleted, added), dc, ac = asyncio.run(run())
    assert deleted == 0
    assert added == 1
    assert len(dc) == 0
    assert len(ac) == 1
    assert ac[0][1] == "A"
    assert "Content A" in ac[0][2]


def test_push_export_deletes_existing_then_adds():
    """When a source with same title exists, delete is called then add_text."""
    deleted_calls = []
    added_calls = []

    class MockSource:
        def __init__(self, id, title):
            self.id = id
            self.title = title

    class MockClient:
        class Sources:
            async def list(self, notebook_id):
                return [MockSource("src-1", "Same Title")]

            async def delete(self, notebook_id, source_id):
                deleted_calls.append((notebook_id, source_id))

            async def add_text(self, notebook_id, title, content, wait=False):
                added_calls.append((notebook_id, title, content))

        sources = Sources()

    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "Same_Title.md"), "w", encoding="utf-8") as f:
                f.write("# Same Title\n\nUpdated content.")
            entries = [{"page_id": "1", "title": "Same Title", "output_path": "Same_Title.md"}]
            client = MockClient()
            return await push_export(client, "nb1", entries, tmp, dry_run=False), deleted_calls, added_calls

    (deleted, added), dc, ac = asyncio.run(run())
    assert deleted == 1
    assert added == 1
    assert len(dc) == 1
    assert dc[0] == ("nb1", "src-1")
    assert len(ac) == 1
    assert ac[0][1] == "Same Title"
    assert "Updated content" in ac[0][2]


def test_push_export_dry_run_no_delete_no_add():
    """Dry run does not call delete or add_text."""
    deleted_calls = []
    added_calls = []

    class MockSource:
        def __init__(self, id, title):
            self.id = id
            self.title = title

    class MockClient:
        class Sources:
            async def list(self, notebook_id):
                return [MockSource("src-1", "Page")]

            async def delete(self, notebook_id, source_id):
                deleted_calls.append((notebook_id, source_id))

            async def add_text(self, notebook_id, title, content, wait=False):
                added_calls.append((notebook_id, title, content))

        sources = Sources()

    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "Page.md"), "w", encoding="utf-8") as f:
                f.write("# Page\n\nContent")
            entries = [{"page_id": "1", "title": "Page", "output_path": "Page.md"}]
            client = MockClient()
            return await push_export(client, "nb1", entries, tmp, dry_run=True), deleted_calls, added_calls

    (deleted, added), dc, ac = asyncio.run(run())
    assert deleted == 1
    assert added == 1
    assert len(dc) == 0
    assert len(ac) == 0
