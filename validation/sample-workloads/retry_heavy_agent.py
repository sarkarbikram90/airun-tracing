"""Sample Workload: Retry-Heavy Workflow to observe retry storm detection and latency penalties."""

import time

from airun import SpanKind, record_retry, set_span_metadata, set_span_tokens, trace


@trace(kind=SpanKind.TOOL, provider="unstable_search_api")
def fetch_external_news(query: str) -> dict:
    time.sleep(0.04)
    # Simulate 3 transient retries
    record_retry()
    record_retry()
    record_retry()
    set_span_metadata({"query": query, "total_attempts": 4})
    return {"articles": ["AI Runtime Profiling Release"]}


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def summarize_news(articles: list[str]) -> str:
    time.sleep(0.08)
    set_span_tokens(input_tokens=1400, output_tokens=180)
    return f"Summarized {len(articles)} articles."


def main():
    with trace("retry_heavy_news_agent", kind=SpanKind.WORKFLOW) as root:
        news = fetch_external_news("AI Agent Economics")
        summary = summarize_news(news["articles"])
        print(f"Summary: {summary} (Trace ID: {root.trace_id[:8]})")


if __name__ == "__main__":
    main()
