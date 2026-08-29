# External Validation — Opportunity & Pain Ranking Matrix

Formula:
$$\text{Opportunity Score} = \text{Frequency (1–10)} \times \text{Severity (1–5)} \times \text{Willingness to Pay (1–5)} \times \text{Technical Feasibility (1–5)}$$

*Maximum Score = 1,250*

| Rank | Recurring Pain Point | Frequency (F, 1-10) | Severity (S, 1-5) | Willingness to Pay (W, 1-5) | Technical Feasibility (T, 1-5) | Opportunity Score | Existing Workaround | Leading Candidate Wedge |
|---|---|---|---|---|---|---|---|---|
| 1 | **Model Inefficiency & Over-Provisioning**: Expensive frontier models called on routine parsing/classification steps | 8 / 10 | 4 / 5 | 4 / 5 | 5 / 5 | **640** | Manual prompt-by-prompt model hardcoding; fear of quality drop | **Wedge 1**: Execution Optimization & Model Routing |
| 2 | **CI/CD Cost Regressions & Silent Loops**: Pull requests introduce recursive calls or bloated prompts that spike cloud bills | 7 / 10 | 4 / 5 | 4 / 5 | 5 / 5 | **560** | In-house Python PR check scripts; end-of-month cloud billing alerts | **Wedge 2**: CI/CD Cost Regression & Budget Guard |
| 3 | **Retry Storms & Flaky Tool Delays**: Unhandled 429s/timeouts burn tokens without circuit breaker ceilings | 8 / 10 | 4 / 5 | 4 / 5 | 4 / 5 | **512** | Custom tenacity/backoff wrappers; ad-hoc try-except loops | **Wedge 3**: Runtime Failure Protection & Circuit Breakers |
| 4 | **Wasted Spend on Failed Workflows**: Multi-step workflows fail at step 8/10, losing 100% of upstream investment | 6 / 10 | 4 / 5 | 3 / 5 | 4 / 5 | **288** | Custom checkpointing in DB; re-running full workflows from scratch | Step Checkpointing & Wasted Cost Monitors |
| 5 | **Token Context Ballooning**: Multi-turn agents accumulate chat histories without automatic pruning | 8 / 10 | 3 / 5 | 3 / 5 | 3 / 5 | **216** | Manual message slicing (`messages[-5:]`); regex string truncators | Context Window Pruner & Summarizer Guard |
| 6 | **Sequential Tool Latency**: Sibling tools executed serially rather than asynchronously | 5 / 10 | 3 / 5 | 3 / 5 | 4 / 5 | **180** | Manual `asyncio.gather` refactoring by senior backend engineers | DAG Interval Optimizer Advice |
| 7 | **Unanticipated Emergent Pain**: Emergent challenge surfaced through validation (e.g. Agent Task Eval Provenance) | — | — | — | — | — | Pending discovery | **Wedge 4**: Emergent Unanticipated Wedge |
