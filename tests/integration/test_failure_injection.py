"""Integration tests for failure injection and error cascades."""

from airun.events.models import SpanKind, SpanStatus
from airun.sdk.tracer import record_retry, trace
from airun.store import get_trace_store


def test_failure_injection_with_retry_and_exception():
    trace_id = None
    caught = False

    try:
        with trace("failure_cascade_workflow", kind=SpanKind.WORKFLOW) as root:
            trace_id = root.trace_id

            # Step 1: Successful setup
            with trace("setup_step", kind=SpanKind.AGENT_STEP):
                pass

            # Step 2: Failing service with retry
            with trace("flaky_service_step", kind=SpanKind.AGENT_STEP):
                record_retry()
                raise ConnectionError("Upstream service unavailable")

    except ConnectionError:
        caught = True

    assert caught
    assert trace_id is not None

    store = get_trace_store()
    rec = store.get_trace(trace_id)
    assert rec is not None
    assert rec.summary.outcome in (SpanStatus.FAILURE, SpanStatus.PARTIAL_SUCCESS)
    assert rec.summary.failed_steps_count >= 1
    assert rec.summary.retry_count >= 1

    flaky_span = [s for s in rec.spans if s.name == "flaky_service_step"][0]
    assert flaky_span.status == SpanStatus.FAILURE
    assert flaky_span.error is not None
    assert "Upstream service unavailable" in flaky_span.error["message"]
