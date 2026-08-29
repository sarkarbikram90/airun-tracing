"""Unit tests for event models."""

from airun.events.models import SpanKind, SpanStatus, TraceSpan, TraceSummary


def test_trace_span_creation():
    span = TraceSpan(
        trace_id="t1",
        span_id="s1",
        name="test_step",
        kind=SpanKind.LLM,
        start_time="2026-08-29T12:00:00Z",
        status=SpanStatus.SUCCESS,
        tokens_input=100,
        tokens_output=200,
    )
    assert span.trace_id == "t1"
    assert span.span_id == "s1"
    assert span.kind == SpanKind.LLM
    assert span.total_tokens == 300
    assert span.retry_count == 0


def test_span_kind_and_status_enums():
    assert SpanKind("workflow") == SpanKind.WORKFLOW
    assert SpanKind("tool") == SpanKind.TOOL
    assert SpanStatus("failure") == SpanStatus.FAILURE
    assert SpanStatus("timeout") == SpanStatus.TIMEOUT


def test_trace_summary_model():
    summary = TraceSummary(
        trace_id="t1",
        name="workflow_1",
        outcome=SpanStatus.SUCCESS,
        start_time="2026-08-29T12:00:00Z",
        total_duration_ms=1250.0,
        total_cost_usd=0.015,
        total_tokens=1500,
    )
    assert summary.trace_id == "t1"
    assert summary.total_cost_usd == 0.015
    assert summary.total_duration_ms == 1250.0
