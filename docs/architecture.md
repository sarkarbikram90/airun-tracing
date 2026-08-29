# System Architecture & Design

`airun` is architected as an ultra-lightweight, local-first measurement layer for agentic and multi-step AI systems.

---

## 1. High-Level Data Flow

```
[ AI Application / Workflow ]
            │
     @trace / with trace()
            │
            ▼
[ airun.sdk.tracer & context ] ──(ContextVar Span Stack)──> [ Privacy & Redaction ]
            │                                                      │
      TraceSpan Event                                       Sanitized Metadata
            │                                                      │
            ▼                                                      ▼
[ airun.store.sqlite / jsonl ] <───────────────────────────────────┘
            │
    Persisted Spans
            │
            ▼
[ airun.graph.builder & critical_path ]
            │
    Directed Execution Tree + Critical Path Traversal
            │
            ▼
[ airun.analysis.analyzer & comparator ]
            │
    Cost, Latency, Failure & Token Metrics
            │
            ▼
[ airun.cli (Typer + Rich) / Exporters (JSON / OTel) ]
```

---

## 2. Core Subsystems

### A. SDK & Context Propagation (`airun.sdk`)
- Utilizes Python `contextvars.ContextVar` to provide coroutine-safe and thread-safe span hierarchy tracking.
- Guarantees zero crash on errors: any telemetry or storage failure outputs a warning to stderr without propagating exceptions into the host workload.
- Supports sync functions, async coroutines, and generator workflows.

### B. Event Model & Storage (`airun.events`, `airun.store`)
- Follows structured Pydantic v2 schemas.
- Local SQLite database (`.airun/traces.db`) with WAL mode enabled for concurrent writes, indexed by `trace_id`, `created_at`, and `outcome`.
- Alternate JSONL store for file-based pipelines and streaming storage.

### C. Execution Graph & Critical Path (`airun.graph`)
- Constructs directed trees (`SpanNode`) mapping root workflows to sub-steps, tools, database queries, and LLM calls.
- Traverses dependency trees to identify the longest non-parallelized execution path (**Critical Path Latency**).

### D. Pricing & Cost Engine (`airun.pricing`)
- Computes token expenses dynamically from configurable pricing dictionaries.
- Supports multi-provider cost tracking (OpenAI, Anthropic, Gemini, Mistral, Local Models).
- Supports hourly infrastructure cost amortization for local/vLLM/SGLang deployments.

### E. Exporters (`airun.exporters`)
- Raw JSON export for programmatic analysis.
- OpenTelemetry 1.0 OTLP-compatible JSON format with GenAI semantic attributes (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`).
