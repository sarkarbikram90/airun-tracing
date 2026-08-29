"""Example: Profiling a workflow with failures and retries."""

import time

from airun import SpanKind, set_span_tokens, trace


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def failing_planner():
    time.sleep(0.05)
    set_span_tokens(input_tokens=500, output_tokens=100)
    return "Execute flaky action"


@trace(kind=SpanKind.TOOL, provider="unreliable_api")
def flaky_external_service():
    time.sleep(0.04)
    # Simulate a failure
    raise ConnectionResetError("Connection dropped by peer after 40ms")


def run_failing_workflow():
    print("Running workflow that encounters an error...")
    try:
        with trace("flaky_customer_pipeline", kind=SpanKind.WORKFLOW) as root:
            failing_planner()
            with trace("api_step", kind=SpanKind.AGENT_STEP):
                flaky_external_service()
    except Exception as e:
        print(f"Caught expected error: {e}")
        print(f"Trace captured with failure details. Trace ID: {root.trace_id}")


if __name__ == "__main__":
    run_failing_workflow()
