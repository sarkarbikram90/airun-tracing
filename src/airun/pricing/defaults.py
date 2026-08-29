"""Default pricing definitions for standard AI models."""

from typing import Any, Dict

# Pricing in USD per 1k tokens (or 1M tokens converted to 1k)
DEFAULT_MODEL_PRICING: Dict[str, Dict[str, Any]] = {
    # OpenAI Models
    "gpt-4o": {
        "input_cost_per_1k_tokens": 0.0025,
        "output_cost_per_1k_tokens": 0.0100,
    },
    "gpt-4o-mini": {
        "input_cost_per_1k_tokens": 0.00015,
        "output_cost_per_1k_tokens": 0.00060,
    },
    "gpt-4-turbo": {
        "input_cost_per_1k_tokens": 0.010,
        "output_cost_per_1k_tokens": 0.030,
    },
    "gpt-4": {
        "input_cost_per_1k_tokens": 0.030,
        "output_cost_per_1k_tokens": 0.060,
    },
    "gpt-3.5-turbo": {
        "input_cost_per_1k_tokens": 0.0005,
        "output_cost_per_1k_tokens": 0.0015,
    },
    "o1": {
        "input_cost_per_1k_tokens": 0.015,
        "output_cost_per_1k_tokens": 0.060,
    },
    "o1-mini": {
        "input_cost_per_1k_tokens": 0.003,
        "output_cost_per_1k_tokens": 0.012,
    },
    "o3-mini": {
        "input_cost_per_1k_tokens": 0.0011,
        "output_cost_per_1k_tokens": 0.0044,
    },
    "text-embedding-3-small": {
        "input_cost_per_1k_tokens": 0.00002,
        "output_cost_per_1k_tokens": 0.0,
    },
    "text-embedding-3-large": {
        "input_cost_per_1k_tokens": 0.00013,
        "output_cost_per_1k_tokens": 0.0,
    },
    # Anthropic Models
    "claude-3-5-sonnet-20241022": {
        "input_cost_per_1k_tokens": 0.003,
        "output_cost_per_1k_tokens": 0.015,
    },
    "claude-3-5-sonnet": {
        "input_cost_per_1k_tokens": 0.003,
        "output_cost_per_1k_tokens": 0.015,
    },
    "claude-3-opus": {
        "input_cost_per_1k_tokens": 0.015,
        "output_cost_per_1k_tokens": 0.075,
    },
    "claude-3-5-haiku": {
        "input_cost_per_1k_tokens": 0.0008,
        "output_cost_per_1k_tokens": 0.004,
    },
    "claude-3-haiku": {
        "input_cost_per_1k_tokens": 0.00025,
        "output_cost_per_1k_tokens": 0.00125,
    },
    # Google Gemini Models
    "gemini-1.5-pro": {
        "input_cost_per_1k_tokens": 0.00125,
        "output_cost_per_1k_tokens": 0.005,
    },
    "gemini-1.5-flash": {
        "input_cost_per_1k_tokens": 0.000075,
        "output_cost_per_1k_tokens": 0.0003,
    },
    "gemini-2.0-flash": {
        "input_cost_per_1k_tokens": 0.0001,
        "output_cost_per_1k_tokens": 0.0004,
    },
    # Open / Mock / Local Models
    "mock-model": {
        "input_cost_per_1k_tokens": 0.0001,
        "output_cost_per_1k_tokens": 0.0004,
    },
    "local-llama-3-8b": {
        "input_cost_per_1k_tokens": 0.0,
        "output_cost_per_1k_tokens": 0.0,
        "estimated_infra_cost_per_hour": 1.20,
    },
    "local-model": {
        "input_cost_per_1k_tokens": 0.0,
        "output_cost_per_1k_tokens": 0.0,
        "estimated_infra_cost_per_hour": 1.0,
    },
}
