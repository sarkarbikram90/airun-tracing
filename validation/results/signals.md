# External Validation — Signal & Integration Requests Log

Track explicit pull from external users: frameworks, integrations, and automation requests.

### Integration Requests
- [ ] **LangChain / LangGraph Auto-Tracer**: Automatic trace extraction without manual `@trace` decoration.
- [ ] **LlamaIndex Query Engine Integration**: Instrument retrieval & node synthesis steps.
- [ ] **CrewAI / AutoGen Multi-Agent Callbacks**: Seamless span hierarchy for multi-agent conversations.
- [ ] **LiteLLM Proxy Hook**: Zero-code network-level trace capture.

### Automation & Control Signals
- [ ] **CI/CD Regression Gate**: `airun compare --max-cost-delta 10% --fail-on-regression`
- [ ] **Automated Model Swap Simulation**: `airun simulate --model gpt-4o-mini` to preview cost reductions.
- [ ] **Circuit Breaker Injector**: Automatically enforce timeout and retry ceilings.
