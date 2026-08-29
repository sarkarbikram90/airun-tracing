# Privacy, Security & Data Redaction

`airun` follows a strict **Privacy-by-Default** and **Local-First** design philosophy.

---

## 1. Privacy Principles

1. **No Content Capture by Default**: Raw prompt texts, completions, and payload bodies are never captured or saved unless explicitly opted in via configuration.
2. **Automatic Secret Redaction**: Sensitive keys (`api_key`, `authorization`, `token`, `password`, `bearer`, `secret`) are automatically detected and masked in metadata dictionaries and string headers.
3. **Local-First**: All telemetry is stored locally in `.airun/traces.db` or `.airun/traces/`. No telemetry is ever transmitted to external cloud servers without explicit user setup.

---

## 2. Configuration (`.airun/config.yaml`)

```yaml
privacy:
  capture_prompt_content: false
  capture_completion_content: false
  capture_tool_inputs: false
  capture_tool_outputs: false
  redact_fields:
    - api_key
    - authorization
    - token
    - password
    - secret
    - bearer
    - client_secret
    - private_key
```
