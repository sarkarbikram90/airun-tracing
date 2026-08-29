"""Unit tests for SQLite and JSONL trace stores."""

from pathlib import Path

from airun.events.models import SpanKind, SpanStatus, TraceRecord, TraceSpan
from airun.store.jsonl import JSONLTraceStore
from airun.store.sqlite import SQLiteTraceStore


def test_sqlite_store_crud(tmp_path: Path):
    db_path = tmp_path / "test.db"
    store = SQLiteTraceStore(db_path)

    span = TraceSpan(
        trace_id="trace_sql_1",
        span_id="span_sql_1",
        name="root_job",
        kind=SpanKind.WORKFLOW,
        start_time="2026-08-29T12:00:00Z",
        status=SpanStatus.SUCCESS,
        duration_ms=250.0,
    )
    rec = TraceRecord(trace_id="trace_sql_1", created_at="2026-08-29T12:00:00Z", spans=[span])

    store.save_trace(rec)

    fetched = store.get_trace("trace_sql_1")
    assert fetched is not None
    assert fetched.trace_id == "trace_sql_1"
    assert len(fetched.spans) == 1
    assert fetched.spans[0].name == "root_job"

    listed = store.list_traces()
    assert len(listed) == 1
    assert listed[0].trace_id == "trace_sql_1"

    deleted = store.delete_trace("trace_sql_1")
    assert deleted is True
    assert store.get_trace("trace_sql_1") is None


def test_jsonl_store_crud(tmp_path: Path):
    storage_dir = tmp_path / "traces_jsonl"
    store = JSONLTraceStore(storage_dir)

    span = TraceSpan(
        trace_id="trace_jsonl_1",
        span_id="span_jsonl_1",
        name="jsonl_workflow",
        kind=SpanKind.WORKFLOW,
        start_time="2026-08-29T12:00:00Z",
        status=SpanStatus.SUCCESS,
        duration_ms=100.0,
    )
    rec = TraceRecord(trace_id="trace_jsonl_1", created_at="2026-08-29T12:00:00Z", spans=[span])

    store.save_trace(rec)

    fetched = store.get_trace("trace_jsonl_1")
    assert fetched is not None
    assert fetched.trace_id == "trace_jsonl_1"
    assert len(fetched.spans) == 1

    listed = store.list_traces()
    assert len(listed) == 1
    assert listed[0].trace_id == "trace_jsonl_1"

    deleted = store.delete_trace("trace_jsonl_1")
    assert deleted is True
    assert store.get_trace("trace_jsonl_1") is None
