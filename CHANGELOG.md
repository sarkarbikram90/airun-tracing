# Changelog

All notable changes to `airun` are documented in this file.

## [0.1.1] - 2026-08-29

### Added
- **`airun run`**: Transparent execution runner that profiles scripts and outputs a post-run summary immediately.
- **`airun doctor`**: Workspace diagnostic command that checks config, storage health, trace count, and micro-overhead.
- **Trace ID Aliases**: `latest`, `last`, `previous`, and `prev` supported across all CLI commands (`report`, `show`, `compare`, `export`).
- **Concurrent DAG Critical Path**: Interval DAG dynamic programming scheduler for accurate critical-path computation across overlapping sibling spans.
- **Actionable Diagnostic Findings**: Rule-based economic and performance insights generated in `airun report` (cost concentration, retry storms, token bloat, over-provisioned models).
- **Cost / Success vs Wasted Cost**: Explicit outcome-based cost attribution calculating wasted dollars on failed/interrupted runs.
- **Trace ID Prefix Matching**: Convenient sub-string lookups for trace IDs in SQLite and JSONL backends.
- **AI Workload Laboratory**: 5 representative agent archetypes in `examples/lab/` with cross-workload comparison runner.
- **External Validation Kit**: Standardized invitation template, checklist, feedback questionnaire, and sample workloads in `validation/`.

## [0.1.0] - 2026-08-29

### Added
- Initial MVP release of `airun`.
- Python SDK with `@trace` decorator and `with trace()` context manager.
- Local SQLite and JSONL trace stores with zero network requirements.
- Cost engine with multi-model pricing (OpenAI, Anthropic, Gemini, local GPU).
- OpenTelemetry OTLP JSON trace exporter.
- Typer CLI with `init`, `demo`, `trace list`, `trace show`, `report`, `compare`, `export`.
- Dockerfile, docker-compose, CI/CD GitHub Actions workflows.
