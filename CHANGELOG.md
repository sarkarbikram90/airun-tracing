# Changelog

All notable changes to `airun` are documented in this file.

## [0.1.2] - 2026-08-30

### Added
- **Interactive Executive Web Dashboard (`airun ui` / `airun serve`)**:
  - Built-in modern dark-mode single-page Web UI displaying high-level FinOps KPIs, execution trace tables, and DAG waterfall timelines.
  - Severity-graded diagnostic findings panel (`[CRITICAL]`, `[WARNING]`, `[INFO]`) highlighting cost concentration, retry storms, and context bloat.
  - Zero-dependency HTTP REST API endpoints (`/api/traces`, `/api/traces/<id>`, `/api/summary`, `/api/compare`, `/healthz`).
  - Resilient networking with automatic port fallback (defaulting to `127.0.0.1:8765`) to prevent Windows socket permission collisions (`WinError 10013`).
- **Real-World Multi-Model Agent Pipeline**:
  - `examples/live_multi_model_agent.py` demonstrating live production agent profiling across Google Gemini (1.5 Flash), OpenAI (GPT-4o), Anthropic (Claude 3.5 Haiku), and Vector DB tools.
  - Automatic fallback simulation when live API keys are not exported in the environment.
- **AWS EKS Deployment Blueprint**:
  - Production-ready Kubernetes manifests in `deploy/kubernetes/` (`pvc.yaml`, `deployment.yaml`, `service.yaml`, `ingress.yaml`, `kustomization.yaml`).
  - AWS Application Load Balancer (ALB) and AWS EBS `gp3` persistent volume configuration.
  - Step-by-step deployment guide in `docs/aws-eks-deployment-guide.md`.
- **GitHub Container Registry (GHCR) Packages Automation**:
  - Multi-stage Docker image automated publishing to `ghcr.io/sarkarbikram90/airun-tracing`.
  - Future release and publishing runbook in `docs/release-guide.md`.

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
