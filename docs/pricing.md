# Pricing Configuration Guide

`airun` includes a built-in cost engine with up-to-date pricing for major AI model providers and supports custom user pricing tables.

---

## 1. Default Pricing Table

Built-in pricing includes:
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`, `o1`, `o1-mini`, `o3-mini`, `text-embedding-3-small`, `text-embedding-3-large`.
- **Anthropic**: `claude-3-5-sonnet`, `claude-3-opus`, `claude-3-5-haiku`, `claude-3-haiku`.
- **Google Gemini**: `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.0-flash`.
- **Local Models**: `local-llama-3-8b`, `mock-model`.

---

## 2. Custom Pricing Configuration

To override or add models, initialize or edit `.airun/pricing.yaml`:

```yaml
models:
  my-fine-tuned-model:
    input_cost_per_1k_tokens: 0.0015
    output_cost_per_1k_tokens: 0.0060

  vllm-llama3-70b-gpu-node:
    input_cost_per_1k_tokens: 0.0
    output_cost_per_1k_tokens: 0.0
    estimated_infra_cost_per_hour: 2.45
```

---

## 3. Cost Calculation Formula

$$\text{Total Cost} = \left(\frac{\text{Input Tokens}}{1000} \times C_{\text{in}}\right) + \left(\frac{\text{Output Tokens}}{1000} \times C_{\text{out}}\right) + \left(\frac{\text{Duration (ms)}}{3,600,000} \times C_{\text{infra/hr}}\right)$$
