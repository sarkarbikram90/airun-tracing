"""Unit tests for analyzer and comparator."""

import json
from pathlib import Path

from airun.analysis.analyzer import analyze_spans
from airun.analysis.comparator import compare_traces
from airun.events.models import SpanStatus, TraceRecord, TraceSpan


def test_analyze_spans_metrics(simple_success_trace: TraceRecord):
    summary = analyze_spans(simple_success_trace.spans)
    assert summary.trace_id == simple_success_trace.trace_id
    assert summary.outcome == SpanStatus.SUCCESS
    assert summary.total_tokens == 1500
    assert summary.llm_call_count == 1
    assert summary.total_cost_usd > 0
    assert len(summary.top_cost_drivers) > 0


def test_analyze_spans_with_retries(retry_trace: TraceRecord):
    summary = analyze_spans(retry_trace.spans)
    assert summary.retry_count >= 2
    assert summary.tool_call_count == 1
    assert summary.llm_call_count == 1


def test_compare_traces_deltas(fixtures_dir: Path):
    path = fixtures_dir / "fixture_cost_comparison.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rec_a = TraceRecord(
        trace_id=data["trace_a"]["trace_id"],
        created_at=data["trace_a"]["created_at"],
        spans=[TraceSpan.model_validate(s) for s in data["trace_a"]["spans"]],
    )
    rec_b = TraceRecord(
        trace_id=data["trace_b"]["trace_id"],
        created_at=data["trace_b"]["created_at"],
        spans=[TraceSpan.model_validate(s) for s in data["trace_b"]["spans"]],
    )

    comp = compare_traces(rec_a, rec_b)
    # Run B is faster and cheaper
    assert comp.delta_duration_ms < 0
    assert comp.delta_cost_usd < 0
    assert comp.delta_retries == -3  # Run A had 3 retries, Run B had 0
    assert len(comp.step_diffs) > 0
