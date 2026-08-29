"""Sample Workload: Offline Mock Agent for Quick Validation."""

import time

from airun import SpanKind, set_span_metadata, set_span_tokens, trace


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def mock_planner(goal: str) -> list[str]:
    time.sleep(0.08)
    set_span_tokens(input_tokens=850, output_tokens=150)
    return ["fetch_metrics", "summarize"]


@trace(kind=SpanKind.TOOL, provider="monitoring_api")
def mock_fetch_metrics(metric_name: str) -> dict:
    time.sleep(0.05)
    set_span_metadata({"metric": metric_name, "points": 100})
    return {"status": "ok", "value": 98.4}


@trace(kind=SpanKind.LLM, model="gpt-4o-mini", provider="openai")
def mock_summarizer(data: dict) -> str:
    time.sleep(0.06)
    set_span_tokens(input_tokens=1200, output_tokens=220)
    return f"System health is optimal at {data['value']}% availability."


def main():
    with trace("sample_mock_agent", kind=SpanKind.WORKFLOW) as root:
        _ = mock_planner("Assess system reliability")
        data = mock_fetch_metrics("cpu_idle")
        summary = mock_summarizer(data)
        print(f"Result: {summary} (Trace ID: {root.trace_id[:8]})")


if __name__ == "__main__":
    main()
