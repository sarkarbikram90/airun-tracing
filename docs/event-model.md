# Event Model & Schema

`airun` represents AI execution paths as structured events inspired by OpenTelemetry concepts.

---

## 1. Span Schema (`TraceSpan`)

```json
{
  "trace_id": "9f2c184e0f314842a2789123456789ab",
  "span_id": "3a1b2c3d4e5f6789",
  "parent_id": "1a2b3c4d5e6f7890",
  "name": "planner_llm_call",
  "kind": "llm",
  "start_time": "2026-08-29T12:00:00.000000+00:00",
  "end_time": "2026-08-29T12:00:00.350000+00:00",
  "duration_ms": 350.0,
  "status": "success",
  "provider": "openai",
  "model": "gpt-4o",
  "tokens_input": 1420,
  "tokens_output": 380,
  "cost_usd": 0.00735,
  "retry_count": 0,
  "error": null,
  "metadata": {
    "temperature": 0.2
  }
}
```

---

## 2. Span Kinds (`SpanKind`)

| Kind | Description |
|---|---|
| `workflow` | The top-level root operation or end-to-end task |
| `agent_step` | An intermediate reasoning, planning, or decision block |
| `llm` | A language model generation or embedding call |
| `tool` | An external tool or function invocation |
| `search` | Web search or retrieval operation |
| `db` | Vector database or relational storage query |
| `http` | External HTTP API request |
| `custom` | Any custom user-defined execution unit |

---

## 3. Span Statuses (`SpanStatus`)

- `success`: Completed without errors.
- `failure`: Encountered an unhandled exception.
- `timeout`: Exceeded maximum allowable timeout limit.
- `retry`: Step was retried due to transient error.
- `partial_success`: Overall workflow succeeded despite partial child step failures.
