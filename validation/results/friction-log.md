# External Validation — Friction & Failure Log

Categorize friction into 4 buckets:
1. **Setup Friction**: Installation failures, missing dependencies, Windows path issues, config confusion.
2. **Conceptual Friction**: Misunderstanding output, metrics ambiguity, finding confusion.
3. **Trust Friction**: Disbelieving cost calculations, token counts, or critical-path timings.
4. **Action Friction**: Seeing the problem but having no clear path or suggestion on how to fix it.

| Date | User ID | Category | Friction Point / Failure Mode | Severity (P0/P1/P2) | Status / Action Taken |
|---|---|---|---|---|---|
| 2026-08-29 | Internal Lab | Setup | Windows charmup console encoding required ASCII-safe status tags | P0 | Fixed in v0.1.1 |
| 2026-08-29 | Internal Lab | Action | Overlapping sibling spans needed Interval DAG critical path resolution | P0 | Fixed in v0.1.1 |
| 2026-08-29 | Internal Lab | Trust | Micro-benchmark trace in `doctor` was appearing in trace history | P1 | Fixed in v0.1.1 (save_on_exit=False) |
