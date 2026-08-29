# Architecture Decision Records (ADRs)

---

## ADR 001: Local-First Storage (SQLite by Default)
- **Context**: AI engineers need fast, zero-configuration local tracing during development and testing without spinning up Postgres, Redis, or external SaaS collectors.
- **Decision**: Use SQLite in WAL mode with indexed trace and span tables. Support JSONL as a flat-file alternative.
- **Consequences**: Zero infrastructure dependencies, instant setup (`< 5s`), portable database files.

---

## ADR 002: Zero-Crash SDK Design
- **Context**: Profiling tools must never bring down production or test agent execution pipelines if logging or disk writing fails.
- **Decision**: All storage operations and metadata serialization steps are guarded with safe exception blocks logging to stderr.
- **Consequences**: 100% execution reliability for the host application.

---

## ADR 003: Critical-Path Latency Calculation
- **Context**: AI workflows often invoke nested, sequential, and parallel tools. Simple sum of durations does not explain the bottleneck.
- **Decision**: Implement tree-based longest non-parallelized traversal to extract exact Critical-Path duration.
- **Consequences**: Engineers immediately see which exact step dictates the user-perceived turnaround time.

---

## ADR 004: OpenTelemetry Compatibility
- **Context**: Production teams eventually export traces to enterprise monitoring systems (Datadog, Honeycomb, Jaeger).
- **Decision**: Build an OpenTelemetry OTLP JSON exporter aligning with OpenTelemetry GenAI semantic conventions.
- **Consequences**: No vendor lock-in; easy migration to central OTel collectors.
