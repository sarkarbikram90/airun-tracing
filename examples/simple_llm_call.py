"""Example: Profiling a simple LLM call with airun."""

import time

from airun import SpanKind, set_span_tokens, trace


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def generate_summary(text: str) -> str:
    # Simulate LLM latency
    time.sleep(0.15)
    # Simulate token usage
    set_span_tokens(input_tokens=450, output_tokens=120)
    return f"Summary of {len(text)} characters text."


def main():
    print("Executing simple LLM workload with airun...")
    with trace("summary_workflow", kind=SpanKind.WORKFLOW) as root:
        result = generate_summary("AI Runtime Profiler is designed to observe agent workflows.")
        print(f"Result: {result}")
        print(f"Trace captured with ID: {root.trace_id}")


if __name__ == "__main__":
    main()
