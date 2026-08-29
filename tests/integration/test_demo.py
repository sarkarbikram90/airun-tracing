"""Integration test for demo agent workflow execution."""

from airun.events.models import SpanKind, SpanStatus
from airun.sdk.tracer import record_retry, set_span_metadata, set_span_tokens, trace
from airun.store import get_trace_store


def test_full_demo_workflow_trace_generation():
    with trace("demo_execution_workflow", kind=SpanKind.WORKFLOW) as root:
        with trace("planning_step", kind=SpanKind.AGENT_STEP):
            with trace("planner_model", kind=SpanKind.LLM, model="gpt-4o", provider="openai"):
                set_span_tokens(input_tokens=1500, output_tokens=300)

        with trace("tool_step", kind=SpanKind.AGENT_STEP):
            with trace("search_tool", kind=SpanKind.TOOL, provider="search_engine"):
                record_retry()
                set_span_metadata({"query": "AI Runtime Tracing", "results": 3})

            with trace("db_tool", kind=SpanKind.DB, provider="sqlite"):
                set_span_metadata({"status": "healthy"})

        with trace("synthesis_step", kind=SpanKind.AGENT_STEP):
            with trace(
                "summarizer_model", kind=SpanKind.LLM, model="gpt-4o-mini", provider="openai"
            ):
                set_span_tokens(input_tokens=2200, output_tokens=450)

    store = get_trace_store()
    rec = store.get_trace(root.trace_id)
    assert rec is not None
    assert rec.summary is not None
    assert rec.summary.outcome == SpanStatus.SUCCESS
    assert rec.summary.llm_call_count == 2
    assert rec.summary.tool_call_count == 1
    assert rec.summary.retry_count >= 1
    assert rec.summary.total_cost_usd > 0
    assert len(rec.spans) == 8
