"""Trace storage package."""

from __future__ import annotations

from typing import Optional

from airun.config import AirunConfig, get_config
from airun.store.base import TraceStore
from airun.store.jsonl import JSONLTraceStore
from airun.store.sqlite import SQLiteTraceStore

_ACTIVE_STORE: Optional[TraceStore] = None


def get_trace_store(config: Optional[AirunConfig] = None) -> TraceStore:
    """Return the configured trace store singleton."""
    global _ACTIVE_STORE
    if _ACTIVE_STORE is not None and config is None:
        return _ACTIVE_STORE

    cfg = config or get_config()
    if cfg.storage_backend == "jsonl":
        _ACTIVE_STORE = JSONLTraceStore(cfg.storage_dir)
    else:
        _ACTIVE_STORE = SQLiteTraceStore(cfg.sqlite_path)

    return _ACTIVE_STORE


def set_trace_store(store: TraceStore) -> None:
    """Override the active trace store (useful for test isolation)."""
    global _ACTIVE_STORE
    _ACTIVE_STORE = store


__all__ = [
    "TraceStore",
    "SQLiteTraceStore",
    "JSONLTraceStore",
    "get_trace_store",
    "set_trace_store",
]
