"""Workload Archetype 3: Tool-Calling Agent with Parallel Tools and Retries."""

from __future__ import annotations

import asyncio
import time

from airun import SpanKind, record_retry, set_span_metadata, set_span_tokens, trace


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def agent_decide_tools(task: str) -> list[str]:
    time.sleep(0.10)
    set_span_tokens(input_tokens=1500, output_tokens=180)
    return ["search_weather", "search_flights", "search_hotels"]


@trace(kind=SpanKind.TOOL, provider="weather_api")
async def call_weather_api(city: str) -> dict:
    await asyncio.sleep(0.06)
    set_span_metadata({"city": city})
    return {"temp_c": 22, "condition": "Sunny"}


@trace(kind=SpanKind.TOOL, provider="flights_api")
async def call_flights_api(origin: str, dest: str) -> dict:
    await asyncio.sleep(0.09)
    # Simulate a transient network retry
    record_retry()
    set_span_metadata({"route": f"{origin}->{dest}", "retries": 1})
    return {"price_usd": 380, "airline": "AirlineX"}


@trace(kind=SpanKind.TOOL, provider="hotels_api")
async def call_hotels_api(city: str) -> dict:
    await asyncio.sleep(0.07)
    set_span_metadata({"city": city})
    return {"hotel": "Grand Hotel", "nightly_rate": 190}


@trace(kind=SpanKind.LLM, model="gpt-4o-mini", provider="openai")
def agent_format_itinerary(results: list) -> str:
    time.sleep(0.08)
    set_span_tokens(input_tokens=2200, output_tokens=320)
    return f"Prepared comprehensive trip plan with {len(results)} booked components."


async def run_tool_agent():
    async with trace("travel_assistant_workflow", kind=SpanKind.WORKFLOW) as root:
        # Step 1: Decision
        _ = agent_decide_tools("Plan vacation to Paris")

        # Step 2: Parallel Tool Execution
        async with trace("parallel_data_fetching", kind=SpanKind.AGENT_STEP):
            weather, flights, hotels = await asyncio.gather(
                call_weather_api("Paris"),
                call_flights_api("JFK", "CDG"),
                call_hotels_api("Paris"),
            )

        # Step 3: Synthesis
        itinerary = agent_format_itinerary([weather, flights, hotels])
        print(
            f"[tool_agent_workload] Finished: {itinerary[:40]}... (Trace ID: {root.trace_id[:8]})"
        )


if __name__ == "__main__":
    asyncio.run(run_tool_agent())
