"""Raw JSON exporter for traces."""

from __future__ import annotations

import json
from typing import Any, Dict

from airun.analysis.analyzer import analyze_spans
from airun.events.models import TraceRecord


def export_trace_to_json(trace_record: TraceRecord, indent: int = 2) -> str:
    """Export a TraceRecord as a formatted JSON string."""
    summary = trace_record.summary or analyze_spans(trace_record.spans)
    data: Dict[str, Any] = {
        "trace_id": trace_record.trace_id,
        "created_at": trace_record.created_at,
        "summary": summary.model_dump(),
        "spans": [s.model_dump() for s in trace_record.spans],
    }
    return json.dumps(data, indent=indent)
