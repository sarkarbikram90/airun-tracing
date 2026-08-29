"""Unit tests for Tracer SDK decorator and context managers."""

from airun.events.models import SpanKind, SpanStatus
from airun.sdk.context import get_current_span_id, get_current_trace_id
from airun.sdk.tracer import (
    record_retry,
    set_span_metadata,
    set_span_tokens,
    trace,
)
from airun.store import get_trace_store


def test_context_manager_tracing():
    with trace("root_workflow", kind=SpanKind.WORKFLOW) as root:
        trace_id = root.trace_id
        assert get_current_trace_id() == trace_id

        with trace("child_llm", kind=SpanKind.LLM, model="gpt-4o") as child:
            assert child.parent_id == root.span_id
            assert get_current_span_id() == child.span_id
            set_span_tokens(input_tokens=100, output_tokens=50)

    # After exit, trace should be saved to store
    store = get_trace_store()
    rec = store.get_trace(trace_id)
    assert rec is not None
    assert len(rec.spans) == 2
    assert rec.spans[0].name == "root_workflow"
    assert rec.spans[1].name == "child_llm"
    assert rec.spans[1].tokens_input == 100
    assert rec.spans[1].tokens_output == 50
    assert rec.spans[1].cost_usd is not None
    assert rec.spans[1].cost_usd > 0


def test_decorator_tracing_sync():
    @trace(kind=SpanKind.TOOL, name="custom_tool")
    def my_tool(x: int) -> int:
        set_span_metadata({"input_arg": x})
        return x * 2

    with trace("workflow_wrapper") as root:
        res = my_tool(21)
        assert res == 42

    store = get_trace_store()
    rec = store.get_trace(root.trace_id)
    assert rec is not None
    assert len(rec.spans) == 2
    assert rec.spans[1].name == "custom_tool"
    assert rec.spans[1].metadata.get("input_arg") == 21


def test_exception_handling_in_tracer():
    caught = False
    trace_id = None
    try:
        with trace("failing_job") as root:
            trace_id = root.trace_id
            with trace("bad_step"):
                raise ValueError("Intentional failure")
    except ValueError:
        caught = True

    assert caught
    assert trace_id is not None
    store = get_trace_store()
    rec = store.get_trace(trace_id)
    assert rec is not None
    assert rec.summary.outcome in (SpanStatus.FAILURE, SpanStatus.PARTIAL_SUCCESS)
    assert rec.spans[1].status == SpanStatus.FAILURE
    assert rec.spans[1].error is not None
    assert "Intentional failure" in rec.spans[1].error["message"]


def test_record_retry_utility():
    with trace("retry_workflow") as root:
        with trace("tool_call", kind=SpanKind.TOOL):
            record_retry()
            record_retry()

    store = get_trace_store()
    rec = store.get_trace(root.trace_id)
    assert rec is not None
    tool_s = [s for s in rec.spans if s.name == "tool_call"][0]
    assert tool_s.retry_count == 2
    assert tool_s.status == SpanStatus.RETRY
