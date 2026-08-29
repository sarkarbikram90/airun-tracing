"""Unit tests for pricing calculations and cost engine."""

from pathlib import Path

import yaml

from airun.pricing.engine import CostEngine, calculate_cost


def test_default_pricing_calculations():
    # gpt-4o: $0.0025 per 1k in, $0.0100 per 1k out
    # 1000 in ($0.0025) + 500 out ($0.0050) = $0.0075
    cost = calculate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
    assert cost is not None
    assert round(cost, 5) == 0.0075


def test_gpt_4o_mini_pricing():
    # gpt-4o-mini: $0.00015 per 1k in, $0.00060 per 1k out
    # 2000 in ($0.00030) + 1000 out ($0.00060) = $0.00090
    cost = calculate_cost("gpt-4o-mini", input_tokens=2000, output_tokens=1000)
    assert cost is not None
    assert round(cost, 5) == 0.00090


def test_claude_sonnet_pricing():
    cost = calculate_cost("claude-3-5-sonnet", input_tokens=1000, output_tokens=1000)
    assert cost is not None
    assert round(cost, 4) == 0.0180  # 0.003 + 0.015


def test_local_model_with_infra_amortization():
    # local-llama-3-8b: estimated infra cost $1.20/hour = $0.0003333/sec
    # 3600 seconds = 3,600,000 ms -> $1.20
    cost = calculate_cost(
        "local-llama-3-8b", input_tokens=10000, output_tokens=5000, duration_ms=3600000.0
    )
    assert cost is not None
    assert round(cost, 2) == 1.20


def test_custom_pricing_yaml(tmp_path: Path):
    custom_yaml = tmp_path / "custom_pricing.yaml"
    data = {
        "models": {
            "my-custom-llm": {
                "input_cost_per_1k_tokens": 0.005,
                "output_cost_per_1k_tokens": 0.020,
            }
        }
    }
    with open(custom_yaml, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    engine = CostEngine(custom_pricing_path=custom_yaml)
    cost = engine.calculate_cost("my-custom-llm", input_tokens=1000, output_tokens=1000)
    assert cost is not None
    assert round(cost, 4) == 0.0250


def test_unknown_model_returns_none():
    cost = calculate_cost(
        "completely-unknown-nonexistent-model-xyz", input_tokens=100, output_tokens=100
    )
    assert cost is None
