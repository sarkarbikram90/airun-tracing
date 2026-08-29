"""Test fixtures and configuration."""

import json
from pathlib import Path

import pytest

from airun.events.models import TraceRecord, TraceSpan
from airun.sdk.context import reset_trace_context
from airun.store import set_trace_store
from airun.store.sqlite import SQLiteTraceStore


@pytest.fixture(autouse=True)
def setup_isolated_store(tmp_path: Path):
    """Provide a fresh SQLite trace store for each test."""
    db_path = tmp_path / "test_traces.db"
    store = SQLiteTraceStore(db_path)
    set_trace_store(store)
    reset_trace_context()
    yield store
    reset_trace_context()


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def simple_success_trace(fixtures_dir: Path) -> TraceRecord:
    path = fixtures_dir / "fixture_simple_success.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    spans = [TraceSpan.model_validate(s) for s in data["spans"]]
    return TraceRecord(
        trace_id=data["trace_id"],
        created_at=data["created_at"],
        spans=spans,
    )


@pytest.fixture
def retry_trace(fixtures_dir: Path) -> TraceRecord:
    path = fixtures_dir / "fixture_with_retry.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    spans = [TraceSpan.model_validate(s) for s in data["spans"]]
    return TraceRecord(
        trace_id=data["trace_id"],
        created_at=data["created_at"],
        spans=spans,
    )
