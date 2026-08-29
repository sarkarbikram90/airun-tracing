"""Abstract base class for trace storage backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from airun.events.models import SpanStatus, TraceRecord, TraceSummary


class TraceStore(ABC):
    """Abstract interface for persisting and querying traces."""

    @abstractmethod
    def save_trace(self, trace_record: TraceRecord) -> None:
        """Persist a complete trace record."""
        pass

    @abstractmethod
    def get_trace(self, trace_id: str) -> Optional[TraceRecord]:
        """Retrieve a full trace record by its ID."""
        pass

    @abstractmethod
    def list_traces(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[SpanStatus] = None,
    ) -> List[TraceSummary]:
        """List summaries of stored traces ordered by creation time descending."""
        pass

    @abstractmethod
    def delete_trace(self, trace_id: str) -> bool:
        """Delete a trace by ID. Returns True if deleted."""
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Clear all stored traces (useful for test resets)."""
        pass
