# External Validation & User Discovery Playbook

> **Mission**: Reach **100 real AI workloads** from external engineers, identify the **1 recurring painful problem**, and validate the transition from *Observability* to *Optimization Intelligence*.

---

## 1. The 100-Workload Tracking Protocol

Track every external execution across representative AI system categories:

| Category | Target Count | Key Metrics to Track | Potential Failure / Spike Vector |
|---|---|---|---|
| **Simple LLM / Chatbot** | 20 | Tokens / req, TTFT, cost / session | Runaway prompt size |
| **RAG Pipelines** | 20 | Embedding cost, top-k retrieval latency, context synthesis cost | Large vector context ingestion |
| **Tool-Augmented Agents** | 20 | Parallel tool latency, retry count, failure penalty | Tool timeouts & retry loops |
| **Coding & Debugger Loops** | 20 | Loop iterations, diff generation cost, test failure frequency | Infinite fix loops |
| **Multi-Agent Systems** | 20 | Agent-to-agent context growth, bottleneck agent span | Compounding token expansion |

---

## 2. The Customer Discovery Interview Script

Do **not** ask: *"Would you use this?"* or *"Do you like the CLI?"*

Ask these 10 diagnostic questions:

1. **"Tell me about the last time an AI workload or agent became unexpectedly expensive or slow."**
2. **"How did you find out?"** *(e.g., end-of-month cloud invoice, user complaints, latency alerts?)*
3. **"How long did it take your team to diagnose the root cause?"**
4. **"What tools did you use during debugging?"** *(e.g., logging print statements, LangSmith, Datadog, raw OpenAI dashboard?)*
5. **"What critical piece of information was missing from those tools?"**
6. **"Who in the organization cared the most about that incident?"** *(e.g., CTO, FinOps, engineering manager, product lead?)*
7. **"What did that incident actually cost the company in dollars or developer hours?"**
8. **"What temporary or permanent workaround did you implement to stop it from happening again?"**
9. **"If a tool automatically warned you about that specific anomaly before it hit production, what would that be worth to your team?"**
10. **"Can we instrument one of your non-sensitive test agent workflows today to see what its execution economics look like?"**

---

## 3. Real-World Optimization Workflow (`airun compare`)

To demonstrate value to external teams, run the **Baseline vs. Optimized** comparison:

### Step 1: Profile Current Baseline
```bash
airun run baseline_agent.py
# Note trace ID: e.g., 9a1b2c3d
```

### Step 2: Implement Targeted Intervention
- Swap extraction or summarization models (`gpt-4` -> `gpt-4o-mini`).
- Enable parallel tool execution with `asyncio.gather`.
- Optimize retrieved context chunk sizes.

### Step 3: Run Optimized Version
```bash
airun run optimized_agent.py
# Note trace ID: e.g., 4e5f6a7b
```

### Step 4: Show the Comparison
```bash
airun compare 9a1b2c3d 4e5f6a7b
```

**Delivers immediate tangible proof of:**
- $\Delta\text{Cost}$ reduction (%)
- $\Delta\text{Latency}$ improvement (%)
- $\Delta\text{Tokens}$ saved
- $\Delta\text{Retries}$ and failure rate stability
