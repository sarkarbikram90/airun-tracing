"""Unit tests for asynchronous tracing with asyncio."""

import asyncio

import pytest

from airun.events.models import SpanKind
from airun.sdk.tracer import set_span_tokens, trace
from airun.store import get_trace_store


@pytest.mark.asyncio
async def test_async_context_manager():
    async with trace("async_root_workflow", kind=SpanKind.WORKFLOW) as root:
        trace_id = root.trace_id
        await asyncio.sleep(0.01)

        async with trace("async_llm_step", kind=SpanKind.LLM, model="gpt-4o-mini"):
            await asyncio.sleep(0.01)
            set_span_tokens(input_tokens=200, output_tokens=80)

    store = get_trace_store()
    rec = store.get_trace(trace_id)
    assert rec is not None
    assert len(rec.spans) == 2
    assert rec.spans[0].name == "async_root_workflow"
    assert rec.spans[1].name == "async_llm_step"
    assert rec.spans[1].parent_id == rec.spans[0].span_id


@pytest.mark.asyncio
async def test_async_decorator():
    @trace(kind=SpanKind.TOOL, name="async_fetch_tool")
    async def async_fetch(url: str) -> dict:
        await asyncio.sleep(0.01)
        return {"url": url, "status": 200}

    async with trace("async_workflow") as root:
        res = await async_fetch("https://api.example.com/data")
        assert res["status"] == 200

    store = get_trace_store()
    rec = store.get_trace(root.trace_id)
    assert rec is not None
    assert len(rec.spans) == 2
    assert rec.spans[1].name == "async_fetch_tool"
