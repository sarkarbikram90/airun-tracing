# AI Runtime Profiler (`airun`)

[![CI](https://github.com/your-org/airun-tracing/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/airun-tracing/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)

> **"What exactly happened during this AI workload, and what did it cost?"**

`airun` is a lightweight, local-first runtime profiler and economic measurement layer for AI agents, multi-step LLM pipelines, and tool-augmented workflows.

---

## Key Features

- **Zero-Friction Tracing**: Instrument functions and async coroutines in seconds with `@trace` or `with trace()`.
- **Accurate Cost Engine**: Automatic token-level cost attribution for OpenAI, Anthropic, Gemini, Mistral, and local GPU infrastructure.
- **Concurrent Critical Path**: Accurately computes critical-path latency across parallel tools using interval DAG scheduling.
- **Automated Diagnostic Findings**: Heuristic detection of cost concentration, retry storms, token context bloat, and over-provisioned models.
- **Outcome-Based Economics**: Explicit attribution of **Cost per Successful Outcome** vs **Wasted Cost** on failed/aborted executions.
- **Regression Diffing (`airun compare`)**: Side-by-side run comparison to detect latency, token, and cost regressions.
- **Privacy by Default**: Automatic secret and API key redaction. Prompt and completion contents are never stored without explicit opt-in.
- **OpenTelemetry Compatible**: Export traces directly as OTLP-compliant JSON.
- **Ultra-Low Overhead**: Measured in-memory span overhead is $<20\mu\text{s}$ and total SQLite persistence overhead is $<1\text{ms}$ per workflow.

---

## 3-Minute Quickstart

### 1. Installation

```bash
pip install airun-profiler
```

### 2. Environment Health Check

```bash
airun doctor
```

### 3. Run the Instant Demo (Zero Setup)

Run an offline multi-step agent simulation without external API keys:

```bash
airun demo
```

Output:
```text
+---------- AI Workflow Runtime Summary -----------+
| Trace ID        5664cdc8296e41d2ab0b1feae7f0d481  |
| Workflow Name   multi_agent_coordination_pipeline |
| Final Outcome   [OK] SUCCESS                      |
| Total Cost      $0.0310                           |
| Cost / Success  $0.0310                           |
| Total Duration  411.7ms                           |
| Critical Path   411.7ms                           |
| Total Tokens    12,170 (in: 10,900, out: 1,270)   |
| Model Calls     4                                 |
| External Calls  2                                 |
| Retries         0                                 |
| Failed Steps    0                                 |
+---------------------------------------------------+

+-------------------- Findings & Optimization Insights ---------------------+
| * [CRITICAL] 56% of total cost comes from step 'agent_researcher' ($0.017)|
| * [WARNING] Token bloat: prompt context grew 2.7x from planner to synthesis|
| * [INFO] Concurrent execution: parallel tools saved ~411ms sequential delay|
+---------------------------------------------------------------------------+

                               Top Cost Drivers                                
+-----------------------------------------------------------------------------+
| #   | Span Name        | Kind | Model / Target    | Cost (USD) | % Total | Duration | Tokens |
|-----+------------------+------+-------------------+------------+---------+----------+--------|
| 1   | agent_researcher | llm  | claude-3-5-sonnet |    $0.0174 |   55.8% |  140.1ms |  3,020 |
| 2   | agent_planner    | llm  | gpt-4o            |    $0.0054 |   21.4% |  100.2ms |  1,590 |
| 3   | agent_critic     | llm  | gemini-1.5-pro    |    $0.0049 |   19.5% |   90.4ms |  3,310 |
| 4   | agent_synth      | llm  | gpt-4o-mini       |    $0.0008 |    3.3% |   80.2ms |  4,250 |
+-----------------------------------------------------------------------------+

Execution Hierarchy:
Execution Trace
`-- [OK] [workflow] multi_agent_coordination_pipeline (411.7ms)
    +-- [OK] [agent_step] agent_planner_phase (100.3ms)
    |   `-- [OK] [llm] agent_planner (100.2ms, model: gpt-4o, 1590 tok, $0.0054)
    +-- [OK] [agent_step] agent_researcher_phase (140.3ms)
    |   `-- [OK] [llm] agent_researcher (140.1ms, model: claude-3-5-sonnet, 3020 tok, $0.0174)
    +-- [OK] [agent_step] agent_critic_phase (90.6ms)
    |   `-- [OK] [llm] agent_critic (90.4ms, model: gemini-1.5-pro, 3310 tok, $0.0049)
    `-- [OK] [agent_step] agent_synthesizer_phase (80.4ms)
        `-- [OK] [llm] agent_synthesizer (80.2ms, model: gpt-4o-mini, 4250 tok, $0.0008)
```

---

## Instrumenting Your Code

### 1. Synchronous Functions

```python
from airun import trace, set_span_tokens, SpanKind

@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def agent_step(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    set_span_tokens(
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
    )
    return response.choices[0].message.content

with trace("customer_support_pipeline", kind=SpanKind.WORKFLOW):
    result = agent_step("Summarize ticket #4821")
```

### 2. Asynchronous Coroutines & Parallel Tools

```python
import asyncio
from airun import trace, SpanKind

async def run_agent():
    async with trace("travel_agent", kind=SpanKind.WORKFLOW):
        # Parallel tools executed concurrently
        async with trace("parallel_booking", kind=SpanKind.AGENT_STEP):
            flights, hotels = await asyncio.gather(
                fetch_flights(),
                fetch_hotels()
            )
```

---

## CLI Reference

| Command | Description |
|---|---|
| `airun doctor` | Verify local workspace, database health, and micro-overhead |
| `airun init` | Initialize workspace configuration and trace storage |
| `airun demo` | Run built-in simulated agent workflow |
| `airun run <script.py>` | Execute Python script with active profiler and instant summary |
| `airun report [latest\|<id>]` | View runtime summary, diagnostic findings, and execution tree |
| `airun compare [previous\|<id1>] [latest\|<id2>]` | Compare two runs and inspect economic/latency deltas |
| `airun trace list` | List stored execution traces |
| `airun trace show [latest\|<id>]` | Inspect execution tree hierarchy |
| `airun export [latest\|<id>] --format [json\|otel-json]` | Export trace in raw JSON or OpenTelemetry format |

---

## AI Workload Laboratory

Explore representative runnable agent archetypes in [`examples/lab/`](examples/lab):
```bash
python examples/lab/run_all.py
```
- `chat_workload.py` — Simple Chatbot
- `rag_workload.py` — RAG Retrieval & Synthesis
- `tool_agent_workload.py` — Tool Agent with Parallel Concurrency & Retries
- `coding_agent_workload.py` — Code Evaluation & Bug Fix Loop
- `multi_agent_workload.py` — Multi-Agent Coordination Pipeline
- `comparison_workload.py` — The Same Workload, Two Ways (Cost & Latency Regression Lab)

---

## External Validation Kit

Preparing to test with external engineering teams? Check the [`validation/`](validation/) directory:
- [Validation Invitation](validation/invitation.md)
- [Quickstart Checklist](validation/quickstart-checklist.md)
- [Feedback Form](validation/feedback-form.md)
- [Friction Log](validation/friction-log.md)

---

## License

Apache 2.0 License. See [LICENSE](LICENSE) for details.
