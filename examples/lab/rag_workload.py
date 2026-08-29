"""Workload Archetype 2: RAG Pipeline (Embedding -> Vector DB -> LLM Synthesis)."""

from __future__ import annotations

import time

from airun import SpanKind, set_span_metadata, set_span_tokens, trace


@trace(kind=SpanKind.LLM, model="text-embedding-3-small", provider="openai")
def generate_query_embedding(query: str) -> list[float]:
    time.sleep(0.04)
    set_span_tokens(input_tokens=len(query) // 4 + 10, output_tokens=0)
    return [0.012, -0.045, 0.089]


@trace(kind=SpanKind.DB, provider="qdrant")
def vector_search(embedding: list[float], top_k: int = 3) -> list[dict]:
    time.sleep(0.06)
    set_span_metadata({"top_k": top_k, "collection": "enterprise_docs"})
    return [
        {"id": "doc_101", "score": 0.92, "content": "airun captures execution traces into SQLite."},
        {"id": "doc_102", "score": 0.88, "content": "Cost engine supports OpenAI and Anthropic."},
    ]


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def synthesize_grounded_answer(query: str, retrieved_docs: list[dict]) -> str:
    time.sleep(0.14)
    context_tokens = sum(len(d["content"]) // 4 for d in retrieved_docs) + 200
    out_tokens = 140
    set_span_tokens(input_tokens=context_tokens + 50, output_tokens=out_tokens)
    return f"Based on {len(retrieved_docs)} docs, airun profiles execution paths and cost."


def run_rag_workload():
    with trace("rag_retrieval_pipeline", kind=SpanKind.WORKFLOW) as root:
        query = "How does airun persist trace spans?"
        emb = generate_query_embedding(query)
        docs = vector_search(emb, top_k=3)
        answer = synthesize_grounded_answer(query, docs)
        print(f"[rag_workload] Finished: {answer[:40]}... (Trace ID: {root.trace_id[:8]})")


if __name__ == "__main__":
    run_rag_workload()
