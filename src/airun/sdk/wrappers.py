"""Client wrappers and auto-instrumentation utilities for OpenAI and HTTP calls."""

from __future__ import annotations

import functools
from typing import Any

from airun.events.models import SpanKind
from airun.sdk.tracer import set_span_model, set_span_tokens, trace


def wrap_openai_client(client: Any) -> Any:
    """
    Wrap an OpenAI client instance (sync or async) to automatically trace
    client.chat.completions.create calls.
    """
    if not hasattr(client, "chat") or not hasattr(client.chat, "completions"):
        return client

    original_create = client.chat.completions.create

    @functools.wraps(original_create)
    def wrapped_create(*args: Any, **kwargs: Any) -> Any:
        model = kwargs.get("model", "unknown-model")
        with trace(name=f"openai_chat_{model}", kind=SpanKind.LLM, provider="openai", model=model):
            set_span_model(model, provider="openai")
            response = original_create(*args, **kwargs)

            # Extract usage if present
            if hasattr(response, "usage") and response.usage:
                in_tok = getattr(response.usage, "prompt_tokens", 0)
                out_tok = getattr(response.usage, "completion_tokens", 0)
                set_span_tokens(input_tokens=in_tok, output_tokens=out_tok)

            return response

    client.chat.completions.create = wrapped_create
    return client
