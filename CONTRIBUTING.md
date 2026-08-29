# Contributing to `airun`

Thank you for your interest in contributing to `airun`!

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/airun-tracing.git
   cd airun-tracing
   ```

2. **Install in editable mode with development dependencies**:
   ```bash
   pip install -e ".[dev,otel]"
   ```

3. **Run the test suite**:
   ```bash
   pytest -v
   ```

4. **Lint and format**:
   ```bash
   ruff check src tests examples
   ruff format src tests examples
   ```

## Pull Request Guidelines

- Ensure all unit, integration, and benchmark tests pass before opening a PR.
- Preserve the **Zero-Crash Guarantee** on SDK entry points.
- Maintain **Privacy-by-Default**: never capture raw prompt/completion text without explicit user configuration.
