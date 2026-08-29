# External User Quickstart Checklist

Follow these 4 steps to profile your first AI workload in under 3 minutes:

- [ ] **Step 1: Install `airun`**
  ```bash
  pip install airun-profiler
  ```

- [ ] **Step 2: Run Health Check & Demo**
  ```bash
  airun doctor
  airun demo
  ```

- [ ] **Step 3: Instrument Your Code**
  ```python
  from airun import trace, set_span_tokens, SpanKind

  with trace("my_agent_job", kind=SpanKind.WORKFLOW):
      # Step 1: Model Call
      with trace("planner", kind=SpanKind.LLM, model="gpt-4o"):
          response = client.chat.completions.create(...)
          set_span_tokens(input_tokens=1200, output_tokens=300)

      # Step 2: Tool Execution
      with trace("custom_tool", kind=SpanKind.TOOL):
          execute_tool(...)
  ```

- [ ] **Step 4: View the Report & Cost Drivers**
  ```bash
  airun report latest
  ```
