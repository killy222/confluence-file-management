"""Tests for push_to_notebooklm (replace-if-exists, PDF upload)."""

import asyncio
import json
import os
import tempfile

import pytest

from push_to_notebooklm import load_manifest, push_export, resolve_path


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
            {"page_id": "1", "title": "One", "output_path": "One.pdf"},
        ]
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        assert load_manifest(tmp) == data


def test_resolve_path_relative():
    """output_path is resolved as export_dir + basename (manifest paths are under export_dir)."""
    assert resolve_path("/app/export", "Page.pdf") == os.path.normpath("/app/export/Page.pdf")
    assert resolve_path("/app/export", "./confluence_export/Page.pdf").endswith("Page.pdf")


def test_push_export_add_only_when_no_existing_sources_uses_add_file():
    """When notebook has no sources, add_file is called (no delete)."""
    deleted_calls = []
    added_calls = []

    class MockClient:
        class Sources:
            async def list(self, notebook_id):
                return []

            async def delete(self, notebook_id, source_id):
                deleted_calls.append((notebook_id, source_id))

            async def add_file(self, notebook_id, path, mime_type=None, wait=False):
                added_calls.append((notebook_id, path, mime_type))

        sources = Sources()

    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "A.pdf"), "wb") as f:
                f.write(b"%PDF-1.4\n%fake\n")
            entries = [{"page_id": "1", "title": "A", "output_path": "A.pdf"}]
            client = MockClient()
            return await push_export(client, "nb1", entries, tmp, dry_run=False), deleted_calls, added_calls

    (deleted, added), dc, ac = asyncio.run(run())
    assert deleted == 0
    assert added == 1
    assert len(dc) == 0
    assert len(ac) == 1
    assert ac[0][1].endswith("A.pdf")
    assert ac[0][2] == "application/pdf"


def test_push_export_deletes_existing_then_adds():
    """When a source with same title exists, delete is called then add_file."""
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

            async def add_file(self, notebook_id, path, mime_type=None, wait=False):
                added_calls.append((notebook_id, path, mime_type))

        sources = Sources()

    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "Same_Title.pdf"), "wb") as f:
                f.write(b"%PDF-1.4\n%fake\n")
            entries = [{"page_id": "1", "title": "Same Title", "output_path": "Same_Title.pdf"}]
            client = MockClient()
            return await push_export(client, "nb1", entries, tmp, dry_run=False), deleted_calls, added_calls

    (deleted, added), dc, ac = asyncio.run(run())
    assert deleted == 1
    assert added == 1
    assert len(dc) == 1
    assert dc[0] == ("nb1", "src-1")
    assert len(ac) == 1
    assert ac[0][1].endswith("Same_Title.pdf")
    assert ac[0][2] == "application/pdf"


def test_push_export_add_file_failure_falls_back_to_add_text(monkeypatch):
    """If add_file raises specific SOURCE_ID error, we fall back to add_text."""
    deleted_calls = []
    added_files = []
    added_texts = []

    class MockSource:
        def __init__(self, id, title):
            self.id = id
            self.title = title

    class MockClient:
        class Sources:
            async def list(self, notebook_id):
                return [MockSource("src-1", "Title")]

            async def delete(self, notebook_id, source_id):
                deleted_calls.append((notebook_id, source_id))

            async def add_file(self, notebook_id, path, mime_type=None, wait=False):
                added_files.append((notebook_id, path, mime_type))
                raise RuntimeError("Failed to get SOURCE_ID from registration response")

            async def add_text(self, notebook_id, title, content, wait=False):
                added_texts.append((notebook_id, title, content))

        sources = Sources()

    async def fake_read_pdf_text(path: str) -> str:
        return "extracted text"

    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "Title.pdf"), "wb") as f:
                f.write(b"%PDF-1.4\n%fake\n")
            entries = [{"page_id": "1", "title": "Title", "output_path": "Title.pdf"}]
            client = MockClient()
            # Patch _read_pdf_text so we don't need pypdf in tests
            monkeypatch.setattr("push_to_notebooklm._read_pdf_text", lambda path: "extracted text")
            return await push_export(client, "nb1", entries, tmp, dry_run=False), deleted_calls, added_files, added_texts

    (deleted, added), dc, af, at = asyncio.run(run())
    assert deleted == 1
    assert added == 1
    # We attempted add_file once and then fell back to add_text.
    assert len(dc) == 1
    assert len(af) == 1
    assert len(at) == 1
    assert at[0][1] == "Title"


def test_push_export_dry_run_no_delete_no_add():
    """Dry run does not call delete or add_file."""
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

            async def add_file(self, notebook_id, path, mime_type=None, wait=False):
                added_calls.append((notebook_id, path, mime_type))

        sources = Sources()

    async def run():
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "Page.pdf"), "wb") as f:
                f.write(b"%PDF-1.4\n%fake\n")
            entries = [{"page_id": "1", "title": "Page", "output_path": "Page.pdf"}]
            client = MockClient()
            return await push_export(client, "nb1", entries, tmp, dry_run=True), deleted_calls, added_calls

    (deleted, added), dc, ac = asyncio.run(run())
    assert deleted == 1
    assert added == 1
    assert len(dc) == 0
    assert len(ac) == 0


def test_truncate_notebook_all_deletes_all_sources():
    """truncate_notebook_all deletes all listed sources and returns count."""
    deleted_calls = []

    class MockSource:
        def __init__(self, id):
            self.id = id

    class MockClient:
        class Sources:
            async def list(self, notebook_id):
                return [MockSource("src-1"), MockSource("src-2")]

            async def delete(self, notebook_id, source_id):
                deleted_calls.append((notebook_id, source_id))

        sources = Sources()

    async def run():
        from push_to_notebooklm import truncate_notebook_all

        client = MockClient()
        count = await truncate_notebook_all(client, "nb1", dry_run=False)
        return count

    count = asyncio.run(run())
    assert count == 2
    assert deleted_calls == [("nb1", "src-1"), ("nb1", "src-2")]


def test_truncate_notebook_all_dry_run_only_counts(capsys):
    """truncate_notebook_all with dry_run logs and does not delete."""
    deleted_calls = []

    class MockSource:
        def __init__(self, id):
            self.id = id

    class MockClient:
        class Sources:
            async def list(self, notebook_id):
                return [MockSource("src-1"), MockSource("src-2"), MockSource("src-3")]

            async def delete(self, notebook_id, source_id):
                deleted_calls.append((notebook_id, source_id))

        sources = Sources()

    async def run():
        from push_to_notebooklm import truncate_notebook_all

        client = MockClient()
        count = await truncate_notebook_all(client, "nb1", dry_run=True)
        return count

    count = asyncio.run(run())
    captured = capsys.readouterr()
    assert count == 3
    assert "Would delete 3 source(s) from notebook nb1" in captured.out
    assert deleted_calls == []
