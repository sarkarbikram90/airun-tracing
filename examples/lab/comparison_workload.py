"""
AI Workload Laboratory — Archetype 6: The Same Workload, Two Ways (Cost & Latency Regression Lab)

Demonstrates side-by-side trace comparison between:
- Run A (Unoptimized): Heavy model (gpt-4o), sequential tools, retry delays, context bloat.
- Run B (Optimized): Light model (gpt-4o-mini), parallel async tools, zero retries, compressed context.
"""

from __future__ import annotations

import asyncio
import time

from rich.console import Console

from airun import (
    SpanKind,
    record_retry,
    set_span_metadata,
    set_span_quality,
    set_span_tokens,
    trace,
)
from airun.analysis.comparator import compare_traces
from airun.cli.formatting import render_comparison_panel
from airun.store import get_trace_store

console = Console()


# --- Run A: Unoptimized Baseline ---
def execute_unoptimized_run() -> str:
    """Execute unoptimized workflow: gpt-4o, sequential tools, retry penalty."""
    with trace("synthesis_pipeline_unoptimized", kind=SpanKind.WORKFLOW) as root:
        # Step 1: Heavy planner
        with trace("agent_planner", kind=SpanKind.LLM, model="gpt-4o", provider="openai"):
            time.sleep(0.12)
            set_span_tokens(input_tokens=2200, output_tokens=450)

        # Step 2: Sequential tool execution with retries
        with trace("search_tool", kind=SpanKind.TOOL, provider="web_search"):
            time.sleep(0.08)
            record_retry()
            set_span_metadata({"query": "AI Runtime Economics", "results": 5})

        with trace("database_tool", kind=SpanKind.DB, provider="postgres"):
            time.sleep(0.06)
            record_retry()
            set_span_metadata({"table": "market_reports", "rows": 12})

        # Step 3: Heavy synthesis with bloated context
        with trace("agent_synthesizer", kind=SpanKind.LLM, model="gpt-4o", provider="openai"):
            time.sleep(0.16)
            set_span_tokens(input_tokens=4800, output_tokens=650)
            set_span_quality(0.94, {"correctness": 0.95, "completeness": 0.93})

    return root.trace_id


# --- Run B: Optimized Architecture ---
async def execute_optimized_run() -> str:
    """Execute optimized workflow: gpt-4o-mini, parallel async tools, zero retries."""
    async with trace("synthesis_pipeline_optimized", kind=SpanKind.WORKFLOW) as root:
        # Step 1: Efficient planner
        async with trace(
            "agent_planner", kind=SpanKind.LLM, model="gpt-4o-mini", provider="openai"
        ):
            await asyncio.sleep(0.04)
            set_span_tokens(input_tokens=950, output_tokens=220)

        # Step 2: Parallel async tools without retries
        async def _fetch_search():
            async with trace("search_tool", kind=SpanKind.TOOL, provider="web_search"):
                await asyncio.sleep(0.05)
                set_span_metadata({"query": "AI Runtime Economics", "results": 5})

        async def _fetch_db():
            async with trace("database_tool", kind=SpanKind.DB, provider="postgres"):
                await asyncio.sleep(0.04)
                set_span_metadata({"table": "market_reports", "rows": 12})

        async with trace("parallel_data_fetch", kind=SpanKind.AGENT_STEP):
            await asyncio.gather(_fetch_search(), _fetch_db())

        # Step 3: Fast synthesis with compressed prompt
        async with trace(
            "agent_synthesizer", kind=SpanKind.LLM, model="gpt-4o-mini", provider="openai"
        ):
            await asyncio.sleep(0.06)
            set_span_tokens(input_tokens=1800, output_tokens=320)
            set_span_quality(0.95, {"correctness": 0.96, "completeness": 0.94})

    return root.trace_id


def run_workload():
    console.print(
        "\n[bold cyan]>> Running Comparison Lab: 'The Same Workload, Two Ways'...[/bold cyan]\n"
    )

    console.print(
        "[dim]1. Executing Run A (Unoptimized: gpt-4o, sequential tools, retries)...[/dim]"
    )
    id_a = execute_unoptimized_run()

    console.print(
        "[dim]2. Executing Run B (Optimized: gpt-4o-mini, parallel async tools, 0 retries)...[/dim]"
    )
    id_b = asyncio.run(execute_optimized_run())

    store = get_trace_store()
    rec_a = store.get_trace(id_a)
    rec_b = store.get_trace(id_b)

    if rec_a and rec_b:
        comp = compare_traces(rec_a, rec_b)
        console.print("\n", render_comparison_panel(comp), "\n")
        console.print(
            f"[dim]Run manually anytime: [bold white]airun compare {id_a[:8]} {id_b[:8]}[/bold white][/dim]\n"
        )


if __name__ == "__main__":
    run_workload()
