"""Critical path and bottleneck analysis in execution graphs with parallel/concurrent execution support."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from airun.graph.builder import ExecutionGraph, SpanNode


def _parse_iso_ms(iso_str: Optional[str]) -> Optional[float]:
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.timestamp() * 1000.0
    except Exception:
        return None


def _compute_children_critical_path(children: List[SpanNode]) -> Tuple[float, List[SpanNode]]:
    """
    Computes the critical path across a set of sibling spans.
    Correctly accounts for parallel/concurrent spans (overlapping in time) vs
    sequential spans (executed one after another).
    """
    if not children:
        return 0.0, []

    if len(children) == 1:
        child_dur = children[0].span.duration_ms or 0.0
        return child_dur, [children[0]]

    # Extract child time intervals
    child_data = []
    has_valid_intervals = True
    for c in children:
        s_ms = _parse_iso_ms(c.span.start_time)
        e_ms = _parse_iso_ms(c.span.end_time)
        dur = c.span.duration_ms or 0.0
        if s_ms is None or e_ms is None:
            has_valid_intervals = False
        child_data.append((c, s_ms, e_ms, dur))

    if not has_valid_intervals:
        # Fallback: find maximum duration among children if intervals cannot be parsed
        best_child = max(children, key=lambda c: c.span.duration_ms or 0.0)
        return best_child.span.duration_ms or 0.0, [best_child]

    # Build sequential dependency DAG between sibling spans
    # An edge u -> v exists if v started at or after u completed (sequential)
    n = len(children)
    # Sort children by start time
    sorted_indices = sorted(
        range(n), key=lambda i: (child_data[i][1] or 0.0, child_data[i][2] or 0.0)
    )

    # Dynamic programming for longest path in DAG
    # dp[i] = (longest_duration_ending_at_i, [path_of_nodes])
    dp: List[Tuple[float, List[SpanNode]]] = [(0.0, []) for _ in range(n)]

    # Tolerance for concurrency overlap (5ms)
    OVERLAP_TOLERANCE_MS = 5.0

    for idx_in_sorted, i in enumerate(sorted_indices):
        c_i, s_i, e_i, dur_i = child_data[i]
        best_prev_dur = 0.0
        best_prev_path: List[SpanNode] = []

        for prev_sorted in range(idx_in_sorted):
            j = sorted_indices[prev_sorted]
            c_j, s_j, e_j, dur_j = child_data[j]

            # Check if j completed before or at i's start (sequential relationship)
            if s_i is not None and e_j is not None and s_i >= (e_j - OVERLAP_TOLERANCE_MS):
                prev_dur, prev_path = dp[j]
                if prev_dur > best_prev_dur:
                    best_prev_dur = prev_dur
                    best_prev_path = prev_path

        dp[i] = (best_prev_dur + dur_i, best_prev_path + [c_i])

    best_total_dur, best_path = max(dp, key=lambda x: x[0])
    return best_total_dur, best_path


def compute_critical_path(graph: ExecutionGraph) -> Tuple[float, List[SpanNode]]:
    """
    Computes the critical path (longest sequential latency path) in the execution graph.
    Returns (critical_path_ms, list of SpanNodes along the path).
    """
    if not graph.roots:
        return 0.0, []

    def _node_critical_path(node: SpanNode) -> Tuple[float, List[SpanNode]]:
        self_dur = node.span.duration_ms or 0.0

        if not node.children:
            return self_dur, [node]

        # Compute critical path through direct children
        child_crit_dur, child_crit_path = _compute_children_critical_path(node.children)

        # Recursively resolve deeper children on the critical child
        if child_crit_path:
            deeper_crit_path = []
            accumulated_child_dur = 0.0
            for c in child_crit_path:
                sub_dur, sub_path = _node_critical_path(c)
                accumulated_child_dur += sub_dur
                deeper_crit_path.extend(sub_path)
        else:
            deeper_crit_path = []
            accumulated_child_dur = child_crit_dur

        # Non-child overhead (time spent in parent outside children)
        direct_child_sum = sum((c.span.duration_ms or 0.0) for c in node.children)
        overhead = max(0.0, self_dur - direct_child_sum)

        total_dur = overhead + accumulated_child_dur
        return total_dur, [node] + deeper_crit_path

    root_paths = [_node_critical_path(r) for r in graph.roots]
    best_root_dur, best_root_path = max(root_paths, key=lambda x: x[0])
    return best_root_dur, best_root_path
