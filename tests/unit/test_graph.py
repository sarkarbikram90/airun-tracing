"""Unit tests for execution graph and critical path calculations."""

from airun.events.models import SpanKind, TraceSpan
from airun.graph.builder import ExecutionGraph
from airun.graph.critical_path import compute_critical_path


def test_execution_graph_tree_construction():
    spans = [
        TraceSpan(
            trace_id="t1",
            span_id="root",
            parent_id=None,
            name="workflow",
            kind=SpanKind.WORKFLOW,
            start_time="2026-08-29T12:00:00.000Z",
            duration_ms=1000.0,
        ),
        TraceSpan(
            trace_id="t1",
            span_id="step1",
            parent_id="root",
            name="plan",
            kind=SpanKind.AGENT_STEP,
            start_time="2026-08-29T12:00:00.100Z",
            duration_ms=400.0,
        ),
        TraceSpan(
            trace_id="t1",
            span_id="step2",
            parent_id="root",
            name="execute",
            kind=SpanKind.AGENT_STEP,
            start_time="2026-08-29T12:00:00.500Z",
            duration_ms=500.0,
        ),
    ]

    graph = ExecutionGraph(spans)
    assert len(graph.roots) == 1
    root_node = graph.primary_root
    assert root_node is not None
    assert root_node.span.span_id == "root"
    assert len(root_node.children) == 2
    assert root_node.children[0].span.span_id == "step1"
    assert root_node.children[1].span.span_id == "step2"


def test_execution_dag_fan_out_and_traversal():
    spans = [
        TraceSpan(
            trace_id="t_dag",
            span_id="root",
            parent_id=None,
            name="workflow",
            kind=SpanKind.WORKFLOW,
            start_time="2026-08-29T12:00:00.000Z",
            duration_ms=1000.0,
        ),
        TraceSpan(
            trace_id="t_dag",
            span_id="tool_a",
            parent_id="root",
            name="fetch_a",
            kind=SpanKind.TOOL,
            start_time="2026-08-29T12:00:00.100Z",
            duration_ms=300.0,
        ),
        TraceSpan(
            trace_id="t_dag",
            span_id="tool_b",
            parent_id="root",
            name="fetch_b",
            kind=SpanKind.TOOL,
            start_time="2026-08-29T12:00:00.100Z",
            duration_ms=400.0,
        ),
    ]

    graph = ExecutionGraph(spans)
    root = graph.primary_root
    assert root is not None
    assert root.is_fan_out is True
    assert set(root.child_ids) == {"tool_a", "tool_b"}

    child_a = graph.nodes_by_id["tool_a"]
    assert child_a.parent_ids == ["root"]
    assert child_a.is_leaf is True

    preorder = graph.walk_preorder()
    assert len(preorder) == 3
    assert preorder[0].span_id == "root"


def test_critical_path_computation():
    spans = [
        TraceSpan(
            trace_id="t1",
            span_id="root",
            parent_id=None,
            name="workflow",
            kind=SpanKind.WORKFLOW,
            start_time="2026-08-29T12:00:00.000Z",
            end_time="2026-08-29T12:00:01.200Z",
            duration_ms=1200.0,
        ),
        TraceSpan(
            trace_id="t1",
            span_id="child_slow",
            parent_id="root",
            name="slow_llm",
            kind=SpanKind.LLM,
            start_time="2026-08-29T12:00:00.100Z",
            end_time="2026-08-29T12:00:01.000Z",
            duration_ms=900.0,
        ),
        TraceSpan(
            trace_id="t1",
            span_id="child_fast",
            parent_id="root",
            name="fast_tool",
            kind=SpanKind.TOOL,
            start_time="2026-08-29T12:00:00.100Z",
            end_time="2026-08-29T12:00:00.300Z",
            duration_ms=200.0,
        ),
    ]

    graph = ExecutionGraph(spans)
    crit_ms, path = compute_critical_path(graph)
    assert crit_ms >= 900.0
    assert any(n.span.span_id == "child_slow" for n in path)


def test_critical_path_parallel_execution():
    """
    Test:
    Parent runs 0.0s -> 0.7s (700ms)
    - Tool A (100ms): 0.0s -> 0.1s [parallel with Tool B]
    - Tool B (300ms): 0.0s -> 0.3s [parallel with Tool A]
    - LLM C (400ms):  0.3s -> 0.7s [sequential after Tool B]

    Critical Path should be:
    Parent -> Tool B (300ms) -> LLM C (400ms) = 700ms, NOT (100 + 300 + 400 = 800ms)
    """
    spans = [
        TraceSpan(
            trace_id="t_parallel",
            span_id="root",
            parent_id=None,
            name="agent_workflow",
            kind=SpanKind.WORKFLOW,
            start_time="2026-08-29T12:00:00.000000+00:00",
            end_time="2026-08-29T12:00:00.700000+00:00",
            duration_ms=700.0,
        ),
        TraceSpan(
            trace_id="t_parallel",
            span_id="tool_a",
            parent_id="root",
            name="tool_fast",
            kind=SpanKind.TOOL,
            start_time="2026-08-29T12:00:00.000000+00:00",
            end_time="2026-08-29T12:00:00.100000+00:00",
            duration_ms=100.0,
        ),
        TraceSpan(
            trace_id="t_parallel",
            span_id="tool_b",
            parent_id="root",
            name="tool_slow",
            kind=SpanKind.TOOL,
            start_time="2026-08-29T12:00:00.000000+00:00",
            end_time="2026-08-29T12:00:00.300000+00:00",
            duration_ms=300.0,
        ),
        TraceSpan(
            trace_id="t_parallel",
            span_id="llm_c",
            parent_id="root",
            name="synthesizer_llm",
            kind=SpanKind.LLM,
            start_time="2026-08-29T12:00:00.300000+00:00",
            end_time="2026-08-29T12:00:00.700000+00:00",
            duration_ms=400.0,
        ),
    ]

    graph = ExecutionGraph(spans)
    crit_ms, path = compute_critical_path(graph)

    # Critical path should equal 700ms (Tool B + LLM C)
    assert round(crit_ms, 1) == 700.0
    path_span_ids = [node.span.span_id for node in path]
    assert "tool_b" in path_span_ids
    assert "llm_c" in path_span_ids
    assert "tool_a" not in path_span_ids
