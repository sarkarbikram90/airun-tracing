# Technical Case Study: Debugging Agent Latency & Cost Spikes

## Scenario
A multi-step financial analysis agent was experiencing escalating OpenAI API bills ($4,200/month) and average response times exceeding 18 seconds.

---

## 1. Before Tracing (The Problem)
- No step-level visibility into agent tool calls or token usage.
- Black-box OpenAI dashboard only showed total daily spend without attributing cost to specific prompts or sub-agents.
- Engineers suspected the vector database was slow.

---

## 2. Tracing with `airun`
The team added `@trace` to the pipeline and inspected with `airun report`:

```text
+---------- AI Workflow Runtime Summary -----------+
| Trace ID        9f2c184e0f314842a2789123456789ab |
| Workflow Name   financial_analysis_agent         |
| Final Outcome   [OK] SUCCESS                     |
| Total Cost      $0.82                            |
| Total Duration  19.4s                            |
| Critical Path   14.2s                            |
| Total Tokens    41,000                           |
| Retries         3                                |
+--------------------------------------------------+

Top Cost Drivers:
1. llm_call / planner_model      $0.61  (74.4%)  13.2s
2. tool_call / web_search_retry  $0.14  (17.1%)   3.8s
3. llm_call / summarizer         $0.07   (8.5%)   1.4s
```

---

## 3. The Root Cause Discovered
1. **Model Mismatch**: The planning agent was using `gpt-4` for simple JSON extraction tasks (costing $0.61 per invocation).
2. **Flaky Search Tool**: The search tool was failing on transient timeouts and triggering 3 sequential retry attempts.

---

## 4. After Optimization & Verification
- Swapped extraction model to `gpt-4o-mini`.
- Fixed search tool timeout settings and caching.

Run comparison with `airun compare`:
```text
Trace Comparison: Baseline vs Optimized
----------------------------------------
Metric          Baseline        Optimized       Delta
Total Duration  19.4s           4.1s            -15.3s (-78.9%)
Total Cost      $0.82           $0.012          -$0.808 (-98.5%)
Tokens          41,000          6,200           -34,800
Retries         3               0               -3
```

**Result**: 98.5% cost reduction and 4.7x faster agent turnaround.
