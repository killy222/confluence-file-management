"""Schema validation tests (no DB required)."""

import pytest
from pydantic import ValidationError

from backend.schemas import TriggerRunsRequest


def test_trigger_runs_request_valid_single():
    req = TriggerRunsRequest(scripts=["confluence_export"])
    assert req.scripts == ["confluence_export"]


def test_trigger_runs_request_valid_chain():
    req = TriggerRunsRequest(scripts=["confluence_export", "notebooklm_push"])
    assert req.scripts == ["confluence_export", "notebooklm_push"]


def test_trigger_runs_request_invalid_script():
    with pytest.raises(ValidationError):
        TriggerRunsRequest(scripts=["invalid_script"])


def test_trigger_runs_request_chain_wrong_order():
    with pytest.raises(ValidationError):
        TriggerRunsRequest(scripts=["notebooklm_push", "confluence_export"])


def test_trigger_runs_request_empty_scripts():
    with pytest.raises(ValidationError):
        TriggerRunsRequest(scripts=[])
