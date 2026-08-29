# 12-Month Post-MVP Evolution Roadmap

Following the progression ladder:
```text
Observe → Explain → Optimize → Control → Automate
```

---

## Months 1–2: Foundation & Runtime Fluency (MVP - Current)
- [x] Python SDK with `@trace` and `with trace()`
- [x] Local SQLite / JSONL trace store
- [x] Directed execution graph & critical path analysis
- [x] Pricing engine & top cost drivers calculation
- [x] Terminal report & run comparator
- [x] OpenTelemetry OTLP JSON export
- [x] Deterministic fixtures & benchmark tests

---

## Months 3–4: Explain Layer & External Validation
- Direct LangChain, LlamaIndex, LiteLLM, and CrewAI auto-instrumentation packages.
- Root-cause anomaly detection (flagging token runaway loops, retry cascades).
- Community pilot with 20 production AI engineering teams.

---

## Months 5–6: Optimize Layer
- Automated model downgrading suggestions (identifying non-critical spans suitable for smaller models).
- Prompt caching potential analysis (predicting savings from OpenAI/Anthropic prompt prefix caching).
- Static HTML report generator (`airun report <id> --html`).

---

## Months 7–9: Control Layer
- Request interception sidecar / proxy mode.
- Dynamic cost budget enforcer (terminating agent loops when cost limit is reached).
- Retry circuit breakers.

---

## Months 10–12: Team & Commercial Platform
- Self-hosted team server & centralized trace aggregator.
- Multi-user RBAC and enterprise compliance auditing.
