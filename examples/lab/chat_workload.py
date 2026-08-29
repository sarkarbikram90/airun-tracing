"""Workload Archetype 1: Simple Chatbot & Context Processing."""

from __future__ import annotations

import time

from airun import SpanKind, set_span_tokens, trace


@trace(kind=SpanKind.LLM, model="gpt-4o-mini", provider="openai")
def chat_response(messages: list[dict]) -> str:
    # Simulate inference latency
    time.sleep(0.08)
    in_tokens = sum(len(m.get("content", "")) // 4 for m in messages) + 120
    out_tokens = 85
    set_span_tokens(input_tokens=in_tokens, output_tokens=out_tokens)
    return "The AI Runtime Profiler observes step execution, retries, and token cost."


def run_chat_workload():
    with trace("simple_chat_session", kind=SpanKind.WORKFLOW) as root:
        messages = [
            {"role": "system", "content": "You are a helpful AI infrastructure assistant."},
            {"role": "user", "content": "What is the primary function of airun?"},
        ]
        answer = chat_response(messages)
        print(f"[chat_workload] Finished: {answer[:40]}... (Trace ID: {root.trace_id[:8]})")


if __name__ == "__main__":
    run_chat_workload()
