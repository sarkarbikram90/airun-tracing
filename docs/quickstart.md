# 5-Minute Quickstart Guide

`airun` is a lightweight, local-first profiler for AI workloads that answers:
> **"What exactly happened during this AI workload, and what did it cost?"**

---

## 1. Installation

Install `airun` via `pip`:

```bash
pip install airun-profiler
```

Or from source:

```bash
git clone https://github.com/your-org/airun-tracing.git
cd airun-tracing
pip install -e .
```

---

## 2. Instant Demo (Zero Setup)

Run the built-in simulated agent workflow without external API keys:

```bash
airun demo
```

You will see:
- High-level executive summary (outcome, total USD cost, tokens, latency, retries)
- Top cost drivers breakdown
- Visual execution tree hierarchy

---

## 3. Instrumenting Your Code

### Using the `@trace` Decorator

```python
from airun import trace, set_span_tokens, SpanKind

@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def call_planner(task: str) -> str:
    # Your model call
    response = openai_client.chat.completions.create(...)
    set_span_tokens(input_tokens=1200, output_tokens=300)
    return response.choices[0].message.content
```

### Using Context Managers

```python
from airun import trace, SpanKind

with trace("customer_agent", kind=SpanKind.WORKFLOW) as root:
    # Step 1
    with trace("planning_step", kind=SpanKind.AGENT_STEP):
        plan = call_planner("Analyze quarterly revenue")

    # Step 2
    with trace("search_tool", kind=SpanKind.TOOL):
        data = search_web("Q3 2026 earnings")
```

---

## 4. CLI Inspection Commands

### List Captured Traces
```bash
airun trace list
```

### Inspect Trace Spans & Tree
```bash
airun trace show <trace_id>
```

### Generate Detailed Report
```bash
airun report <trace_id>
```

### Compare Two Runs (Regression Detection)
```bash
airun compare <baseline_trace_id> <optimized_trace_id>
```

### Export Trace (JSON or OpenTelemetry)
```bash
airun export <trace_id> --format json --output trace.json
airun export <trace_id> --format otel-json --output otel_trace.json
```
