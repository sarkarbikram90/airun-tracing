"""Workload Archetype 5: Multi-Agent System (Planner -> Researcher -> Critic -> Synthesizer)."""

from __future__ import annotations

import time

from airun import SpanKind, set_span_tokens, trace


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def agent_planner(goal: str) -> dict:
    time.sleep(0.10)
    set_span_tokens(input_tokens=1400, output_tokens=190)
    return {"hypothesis": "AI execution graphs optimize runtime costs", "subtasks": 3}


@trace(kind=SpanKind.LLM, model="claude-3-5-sonnet", provider="anthropic")
def agent_researcher(hypothesis: str) -> list[str]:
    time.sleep(0.14)
    set_span_tokens(input_tokens=2600, output_tokens=420)
    return [
        "Finding 1: LLM token costs account for 78% of overall agent spend.",
        "Finding 2: 24% of latency is non-critical path tool overhead.",
    ]


@trace(kind=SpanKind.LLM, model="gemini-1.5-pro", provider="google")
def agent_critic(findings: list[str]) -> dict:
    time.sleep(0.09)
    set_span_tokens(input_tokens=3100, output_tokens=210)
    return {"approved": True, "critique": "Evidence is robust; proceed to executive summary."}


@trace(kind=SpanKind.LLM, model="gpt-4o-mini", provider="openai")
def agent_synthesizer(findings: list[str], critique: dict) -> str:
    time.sleep(0.08)
    set_span_tokens(input_tokens=3800, output_tokens=450)
    return f"Executive Report: Validated hypothesis with approval: {critique['approved']}"


def run_multi_agent_system():
    with trace("multi_agent_coordination_pipeline", kind=SpanKind.WORKFLOW) as root:
        # Agent 1: Planner
        with trace("agent_planner_phase", kind=SpanKind.AGENT_STEP):
            plan = agent_planner("Analyze multi-agent economic trade-offs")

        # Agent 2: Researcher
        with trace("agent_researcher_phase", kind=SpanKind.AGENT_STEP):
            findings = agent_researcher(plan["hypothesis"])

        # Agent 3: Critic / Verifier
        with trace("agent_critic_phase", kind=SpanKind.AGENT_STEP):
            review = agent_critic(findings)

        # Agent 4: Synthesizer
        with trace("agent_synthesizer_phase", kind=SpanKind.AGENT_STEP):
            final_report = agent_synthesizer(findings, review)

        print(
            f"[multi_agent_workload] Complete: {final_report[:40]}... (Trace ID: {root.trace_id[:8]})"
        )


if __name__ == "__main__":
    run_multi_agent_system()
