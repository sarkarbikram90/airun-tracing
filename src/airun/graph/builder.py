"""Directed Acyclic Graph (DAG) builder for workflow execution tracing."""

from __future__ import annotations

from typing import Dict, List, Optional

from airun.events.models import TraceSpan


class SpanNode:
    """A node in the execution DAG."""

    def __init__(self, span: TraceSpan, parent: Optional[SpanNode] = None):
        self.span = span
        self.span_id = span.span_id
        self.parent = parent
        self.parents: List[SpanNode] = [parent] if parent else []
        self.children: List[SpanNode] = []

    @property
    def child_ids(self) -> List[str]:
        return [c.span_id for c in self.children]

    @property
    def parent_ids(self) -> List[str]:
        return [p.span_id for p in self.parents]

    def add_child(self, child: SpanNode) -> None:
        """Attach a child node with reciprocal parent linkage."""
        if child not in self.children:
            self.children.append(child)
        if self not in child.parents:
            child.parents.append(self)
        child.parent = self

    @property
    def is_root(self) -> bool:
        return len(self.parents) == 0

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def is_fan_out(self) -> bool:
        """Return True if this node launches multiple parallel/concurrent children."""
        return len(self.children) > 1

    @property
    def is_join(self) -> bool:
        """Return True if this node joins multiple parent dependencies."""
        return len(self.parents) > 1

    def get_descendants(self) -> List[SpanNode]:
        """Return a flat list of all descendant nodes in depth-first traversal."""
        descendants = []
        visited = set()

        def _traverse(node: SpanNode) -> None:
            for child in node.children:
                if child.span_id not in visited:
                    visited.add(child.span_id)
                    descendants.append(child)
                    _traverse(child)

        _traverse(self)
        return descendants

    def __repr__(self) -> str:
        return (
            f"SpanNode(id={self.span_id[:6]}, name={self.span.name!r}, "
            f"kind={self.span.kind.value if hasattr(self.span.kind, 'value') else self.span.kind!r}, "
            f"children={len(self.children)}, parents={len(self.parents)})"
        )


class ExecutionGraph:
    """Directed Acyclic Graph (DAG) representing an entire workflow execution."""

    def __init__(self, spans: List[TraceSpan]):
        self.spans = spans
        self.nodes_by_id: Dict[str, SpanNode] = {}
        self.roots: List[SpanNode] = []
        self._build_graph()

    def _build_graph(self) -> None:
        """Build DAG nodes and wire dependencies from spans."""
        # 1. Instantiate all nodes
        for span in self.spans:
            self.nodes_by_id[span.span_id] = SpanNode(span)

        # 2. Wire parent-child relationships
        for span in self.spans:
            node = self.nodes_by_id[span.span_id]
            if span.parent_id and span.parent_id in self.nodes_by_id:
                parent_node = self.nodes_by_id[span.parent_id]
                parent_node.add_child(node)
            else:
                self.roots.append(node)

    @property
    def primary_root(self) -> Optional[SpanNode]:
        """Get the primary root node of the trace."""
        return self.roots[0] if self.roots else None

    def walk_preorder(self) -> List[SpanNode]:
        """Traverse the DAG in pre-order depth-first without repeating nodes."""
        ordered: List[SpanNode] = []
        visited = set()

        def _walk(node: SpanNode) -> None:
            if node.span_id not in visited:
                visited.add(node.span_id)
                ordered.append(node)
                for child in node.children:
                    _walk(child)

        for root in self.roots:
            _walk(root)

        return ordered
