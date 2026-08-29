"""JSONL flat-file trace storage backend."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from airun.analysis.analyzer import analyze_spans
from airun.events.models import SpanStatus, TraceRecord, TraceSummary
from airun.store.base import TraceStore


class JSONLTraceStore(TraceStore):
    """File-based JSONL store where each trace is stored in a .jsonl file."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_trace_file(self, trace_id: str) -> Path:
        return self.storage_dir / f"{trace_id}.jsonl"

    def save_trace(self, trace_record: TraceRecord) -> None:
        if not trace_record.spans:
            return

        summary = trace_record.summary or analyze_spans(trace_record.spans)
        trace_record.summary = summary

        trace_file = self._get_trace_file(trace_record.trace_id)
        with open(trace_file, "w", encoding="utf-8") as f:
            # First line: Metadata header with summary
            header = {
                "type": "trace_header",
                "trace_id": trace_record.trace_id,
                "created_at": trace_record.created_at,
                "summary": summary.model_dump(),
            }
            f.write(json.dumps(header) + "\n")

            # Subsequent lines: Spans
            for span in trace_record.spans:
                span_data = {"type": "span", "data": span.model_dump()}
                f.write(json.dumps(span_data) + "\n")

    def get_trace(self, trace_id: str) -> Optional[TraceRecord]:
        trace_file = self._get_trace_file(trace_id)
        if not trace_file.exists():
            # Check for prefix match
            matching = list(self.storage_dir.glob(f"{trace_id}*.jsonl"))
            if matching:
                trace_file = matching[0]
                trace_id = trace_file.stem
            else:
                return None

        spans = []
        summary = None
        created_at = ""

        with open(trace_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                if item.get("type") == "trace_header":
                    created_at = item.get("created_at", "")
                    if item.get("summary"):
                        summary = TraceSummary.model_validate(item["summary"])
                elif item.get("type") == "span":
                    spans.append(item["data"])

        from airun.events.models import TraceSpan

        parsed_spans = [TraceSpan.model_validate(s) for s in spans]
        if summary is None and parsed_spans:
            summary = analyze_spans(parsed_spans)

        return TraceRecord(
            trace_id=trace_id,
            created_at=created_at,
            spans=parsed_spans,
            summary=summary,
        )

    def list_traces(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[SpanStatus] = None,
    ) -> List[TraceSummary]:
        files = sorted(
            self.storage_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        summaries: List[TraceSummary] = []

        for p in files:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    first_line = f.readline()
                    if not first_line:
                        continue
                    item = json.loads(first_line)
                    if item.get("type") == "trace_header" and item.get("summary"):
                        summary = TraceSummary.model_validate(item["summary"])
                        if status and summary.outcome != status:
                            continue
                        summaries.append(summary)
            except Exception:
                continue

        return summaries[offset : offset + limit]

    def delete_trace(self, trace_id: str) -> bool:
        trace_file = self._get_trace_file(trace_id)
        if trace_file.exists():
            trace_file.unlink()
            return True
        return False

    def clear_all(self) -> None:
        for p in self.storage_dir.glob("*.jsonl"):
            p.unlink()
