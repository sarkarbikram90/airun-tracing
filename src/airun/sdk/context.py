"""Context and state management for active traces and spans."""

from __future__ import annotations

import contextvars
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from airun.events.models import TraceSpan

# ContextVars for async-safe and thread-safe execution tracking
_ACTIVE_TRACE_ID: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "active_trace_id", default=None
)
_ACTIVE_SPAN_STACK: contextvars.ContextVar[Optional[List[TraceSpan]]] = contextvars.ContextVar(
    "active_span_stack", default=None
)
_COLLECTED_SPANS: contextvars.ContextVar[Optional[List[TraceSpan]]] = contextvars.ContextVar(
    "collected_spans", default=None
)


def get_current_trace_id() -> Optional[str]:
    """Get the currently executing trace ID."""
    return _ACTIVE_TRACE_ID.get()


def set_current_trace_id(trace_id: Optional[str]) -> None:
    """Set the currently executing trace ID."""
    _ACTIVE_TRACE_ID.set(trace_id)


def get_current_span() -> Optional[TraceSpan]:
    """Get the current active parent span from the top of the stack."""
    stack = _ACTIVE_SPAN_STACK.get()
    return stack[-1] if stack else None


def get_current_span_id() -> Optional[str]:
    """Get the ID of the current active span."""
    span = get_current_span()
    return span.span_id if span else None


def push_span(span: TraceSpan) -> None:
    """Push a new span onto the execution stack."""
    stack = list(_ACTIVE_SPAN_STACK.get() or [])
    stack.append(span)
    _ACTIVE_SPAN_STACK.set(stack)

    # Also register into collected spans for this trace
    collected = list(_COLLECTED_SPANS.get() or [])
    collected.append(span)
    _COLLECTED_SPANS.set(collected)


def pop_span() -> Optional[TraceSpan]:
    """Pop the active span from the execution stack."""
    stack = list(_ACTIVE_SPAN_STACK.get() or [])
    if not stack:
        return None
    popped = stack.pop()
    _ACTIVE_SPAN_STACK.set(stack)
    return popped


def get_collected_spans() -> List[TraceSpan]:
    """Retrieve all spans recorded for the current trace session."""
    return list(_COLLECTED_SPANS.get() or [])


def reset_trace_context() -> None:
    """Clear trace context and collected spans."""
    _ACTIVE_TRACE_ID.set(None)
    _ACTIVE_SPAN_STACK.set(None)
    _COLLECTED_SPANS.set(None)
