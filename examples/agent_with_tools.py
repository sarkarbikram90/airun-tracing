"""Example: Profiling a multi-step agent with tools and database lookup."""

import time

from airun import SpanKind, set_span_metadata, set_span_tokens, trace


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def agent_planner(prompt: str) -> list[str]:
    time.sleep(0.12)
    set_span_tokens(input_tokens=1200, output_tokens=250)
    return ["search_docs", "query_db", "synthesize"]


@trace(kind=SpanKind.TOOL, provider="search_api")
def search_tool(query: str) -> dict:
    time.sleep(0.08)
    set_span_metadata({"query": query, "hits": 3})
    return {"status": "ok", "documents": ["doc1", "doc2"]}


@trace(kind=SpanKind.DB, provider="sqlite_local")
def query_database(doc_id: str) -> dict:
    time.sleep(0.04)
    set_span_metadata({"doc_id": doc_id})
    return {"id": doc_id, "data": "Sample content from memory"}


@trace(kind=SpanKind.LLM, model="gpt-4o-mini", provider="openai")
def agent_synthesizer(data: list) -> str:
    time.sleep(0.10)
    set_span_tokens(input_tokens=3100, output_tokens=650)
    return f"Synthesized answer based on {len(data)} sources."


def run_agent():
    with trace("multi_step_agent_job", kind=SpanKind.WORKFLOW) as workflow_span:
        # Step 1: Plan
        _ = agent_planner("Research market dynamics for AI runtime profilers")

        # Step 2: Tools
        with trace("tool_execution_phase", kind=SpanKind.AGENT_STEP):
            docs = search_tool("AI observability market size")
            db_res = query_database("doc1")

        # Step 3: Synthesis
        answer = agent_synthesizer([docs, db_res])
        print(f"Final Agent Answer: {answer}")
        print(f"Captured Trace ID: {workflow_span.trace_id}")


if __name__ == "__main__":
    run_agent()
