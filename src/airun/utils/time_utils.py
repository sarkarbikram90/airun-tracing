"""Time and formatting utilities."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional


def now_utc_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def perf_counter_ms() -> float:
    """Return high-resolution monotonic time in milliseconds."""
    return time.perf_counter() * 1000.0


def format_duration(ms: float) -> str:
    """Format milliseconds into a human-friendly string (ms, s, min)."""
    if ms < 1000.0:
        return f"{ms:.1f}ms"
    sec = ms / 1000.0
    if sec < 60.0:
        return f"{sec:.2f}s"
    minutes = int(sec // 60)
    remaining_sec = sec % 60
    return f"{minutes}m {remaining_sec:.1f}s"


def format_cost(cost: Optional[float]) -> str:
    """Format cost in USD."""
    if cost is None:
        return "unknown"
    if cost == 0.0:
        return "$0.00"
    if cost < 0.0001:
        return f"${cost:.6f}"
    if cost < 0.01:
        return f"${cost:.4f}"
    return f"${cost:.2f}"
