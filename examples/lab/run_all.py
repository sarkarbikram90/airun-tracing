"""AI Workload Laboratory: Batch Runner & Cross-Workload Analysis."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure root directory is in python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import all 6 archetypes
from examples.lab.chat_workload import run_chat_workload
from examples.lab.coding_agent_workload import run_coding_agent
from examples.lab.comparison_workload import run_workload as run_comparison_workload
from examples.lab.multi_agent_workload import run_multi_agent_system
from examples.lab.rag_workload import run_rag_workload
from examples.lab.tool_agent_workload import run_tool_agent
from rich.console import Console
from rich.table import Table

from airun.store import get_trace_store
from airun.utils.time_utils import format_cost, format_duration

console = Console()


def run_laboratory():
    console.print(
        "\n[bold cyan]>> Running AI Workload Laboratory (6 Representative Archetypes)...[/bold cyan]\n"
    )

    # 1. Simple Chat
    run_chat_workload()

    # 2. RAG Pipeline
    run_rag_workload()

    # 3. Tool Agent
    asyncio.run(run_tool_agent())

    # 4. Coding Agent
    run_coding_agent()

    # 5. Multi-Agent System
    run_multi_agent_system()

    # 6. Comparison Lab (The Same Workload, Two Ways)
    run_comparison_workload()

    # Fetch last 7 traces from store (including both runs from comparison)
    store = get_trace_store()
    traces = store.list_traces(limit=7)

    console.print(
        "\n[bold green]Laboratory Execution Complete! Cross-Workload Profile:[/bold green]\n"
    )

    table = Table(
        title="[bold cyan]AI Workload Laboratory: Profile Comparison[/bold cyan]",
        border_style="bright_blue",
    )
    table.add_column("Workload Name", style="bold white", min_width=25)
    table.add_column("Outcome", justify="center")
    table.add_column("Duration", justify="right", style="magenta")
    table.add_column("Critical Path", justify="right", style="yellow")
    table.add_column("Cost (USD)", justify="right", style="bold green")
    table.add_column("Tokens", justify="right", style="blue")
    table.add_column("Model Calls", justify="center")
    table.add_column("Tool Calls", justify="center")
    table.add_column("Retries", justify="center", style="yellow")

    for t in reversed(traces):
        outcome_style = "bold green" if t.outcome.value == "success" else "bold yellow"
        table.add_row(
            t.name,
            f"[{outcome_style}]{t.outcome.value.upper()}[/{outcome_style}]",
            format_duration(t.total_duration_ms),
            format_duration(t.critical_path_ms),
            format_cost(t.total_cost_usd),
            f"{t.total_tokens:,}",
            str(t.llm_call_count),
            str(t.tool_call_count),
            str(t.retry_count),
        )

    console.print(table)
    console.print()


if __name__ == "__main__":
    run_laboratory()
