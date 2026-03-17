"""Tests for NotebookSource model shape (no DB required)."""

from backend.models import NotebookSource, NotebookTarget


def test_notebook_source_has_expected_fields():
    ns = NotebookSource(
        notebook_target_id="00000000-0000-0000-0000-000000000000",
        page_id="123",
        title="Sample Page",
        notebook_source_id="source-abc",
    )

    # Basic attribute presence checks
    assert ns.notebook_target_id
    assert ns.page_id == "123"
    assert ns.title == "Sample Page"
    assert ns.notebook_source_id == "source-abc"


def test_notebook_source_relationship_to_notebook_target():
    target = NotebookTarget(name="Test Notebook")
    ns = NotebookSource(
        notebook_target=target,
        page_id="123",
        title="Sample Page",
        notebook_source_id="source-abc",
    )

    assert ns.notebook_target is target

