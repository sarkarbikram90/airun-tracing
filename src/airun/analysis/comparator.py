"""Comparison engine for diffing two execution traces."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from airun.analysis.analyzer import analyze_spans
from airun.events.models import TraceRecord, TraceSummary


class StepDiff(BaseModel):
    name: str
    kind: str
    duration_a_ms: Optional[float] = None
    duration_b_ms: Optional[float] = None
    cost_a_usd: Optional[float] = None
    cost_b_usd: Optional[float] = None
    tokens_a: Optional[int] = None
    tokens_b: Optional[int] = None


class TraceComparison(BaseModel):
    trace_a_id: str
    trace_b_id: str
    summary_a: TraceSummary
    summary_b: TraceSummary

    delta_duration_ms: float
    delta_duration_pct: float
    delta_cost_usd: float
    delta_cost_pct: float
    delta_tokens: int
    delta_retries: int
    delta_failures: int
    delta_quality_score: Optional[float] = None

    step_diffs: List[StepDiff] = Field(default_factory=list)


def compare_traces(trace_a: TraceRecord, trace_b: TraceRecord) -> TraceComparison:
    """Compare two traces and calculate performance and cost deltas."""
    summary_a = trace_a.summary or analyze_spans(trace_a.spans)
    summary_b = trace_b.summary or analyze_spans(trace_b.spans)

    delta_dur = summary_b.total_duration_ms - summary_a.total_duration_ms
    pct_dur = (
        (delta_dur / summary_a.total_duration_ms * 100.0)
        if summary_a.total_duration_ms > 0
        else 0.0
    )

    delta_cost = summary_b.total_cost_usd - summary_a.total_cost_usd
    pct_cost = (
        (delta_cost / summary_a.total_cost_usd * 100.0) if summary_a.total_cost_usd > 0 else 0.0
    )

    delta_tokens = summary_b.total_tokens - summary_a.total_tokens
    delta_retries = summary_b.retry_count - summary_a.retry_count
    delta_failures = summary_b.failed_steps_count - summary_a.failed_steps_count

    delta_quality: Optional[float] = None
    if summary_a.quality_score is not None and summary_b.quality_score is not None:
        delta_quality = round(summary_b.quality_score - summary_a.quality_score, 3)

    # Build step-level diffs
    steps_a = {s.name: s for s in trace_a.spans}
    steps_b = {s.name: s for s in trace_b.spans}
    all_step_names = list(dict.fromkeys(list(steps_a.keys()) + list(steps_b.keys())))

    step_diffs: List[StepDiff] = []
    for name in all_step_names:
        sa = steps_a.get(name)
        sb = steps_b.get(name)
        kind = sa.kind.value if sa else (sb.kind.value if sb else "custom")
        step_diffs.append(
            StepDiff(
                name=name,
                kind=kind,
                duration_a_ms=sa.duration_ms if sa else None,
                duration_b_ms=sb.duration_ms if sb else None,
                cost_a_usd=sa.cost_usd if sa else None,
                cost_b_usd=sb.cost_usd if sb else None,
                tokens_a=sa.total_tokens if sa else None,
                tokens_b=sb.total_tokens if sb else None,
            )
        )

    return TraceComparison(
        trace_a_id=summary_a.trace_id,
        trace_b_id=summary_b.trace_id,
        summary_a=summary_a,
        summary_b=summary_b,
        delta_duration_ms=round(delta_dur, 2),
        delta_duration_pct=round(pct_dur, 2),
        delta_cost_usd=round(delta_cost, 6),
        delta_cost_pct=round(pct_cost, 2),
        delta_tokens=delta_tokens,
        delta_retries=delta_retries,
        delta_failures=delta_failures,
        delta_quality_score=delta_quality,
        step_diffs=step_diffs,
    )
