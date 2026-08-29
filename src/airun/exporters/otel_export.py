"""OpenTelemetry (OTel) OTLP-compatible JSON exporter."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from airun.events.models import SpanKind, SpanStatus, TraceRecord, TraceSpan


def _to_unix_nano(iso_str: Optional[str]) -> str:
    if not iso_str:
        return "0"
    try:
        dt = datetime.fromisoformat(iso_str)
        return str(int(dt.timestamp() * 1_000_000_000))
    except Exception:
        return "0"


def _format_otlp_attr_value(val: Any) -> Dict[str, Any]:
    if isinstance(val, bool):
        return {"boolValue": val}
    elif isinstance(val, int):
        return {"intValue": str(val)}
    elif isinstance(val, float):
        return {"doubleValue": val}
    elif isinstance(val, (dict, list)):
        return {"stringValue": json.dumps(val)}
    else:
        return {"stringValue": str(val)}


def _span_to_otlp(span: TraceSpan) -> Dict[str, Any]:
    # Convert trace_id and span_id to fixed length hex if needed
    trace_hex = span.trace_id.replace("-", "").ljust(32, "0")[:32]
    span_hex = span.span_id.replace("-", "").ljust(16, "0")[:16]
    parent_hex = span.parent_id.replace("-", "").ljust(16, "0")[:16] if span.parent_id else ""

    # Kind mapping
    kind_int = 1  # SPAN_KIND_INTERNAL
    if span.kind in (SpanKind.LLM, SpanKind.HTTP, SpanKind.SEARCH):
        kind_int = 3  # SPAN_KIND_CLIENT
    elif span.kind == SpanKind.WORKFLOW:
        kind_int = 2  # SPAN_KIND_SERVER

    attributes: List[Dict[str, Any]] = [
        {
            "key": "airun.kind",
            "value": {
                "stringValue": span.kind.value if hasattr(span.kind, "value") else str(span.kind)
            },
        },
        {"key": "airun.retry_count", "value": {"intValue": str(span.retry_count)}},
    ]

    if span.provider:
        attributes.append({"key": "gen_ai.system", "value": {"stringValue": span.provider}})
    if span.model:
        attributes.append({"key": "gen_ai.request.model", "value": {"stringValue": span.model}})
    if span.tokens_input is not None:
        attributes.append(
            {"key": "gen_ai.usage.input_tokens", "value": {"intValue": str(span.tokens_input)}}
        )
    if span.tokens_output is not None:
        attributes.append(
            {"key": "gen_ai.usage.output_tokens", "value": {"intValue": str(span.tokens_output)}}
        )
    if span.cost_usd is not None:
        attributes.append({"key": "airun.cost_usd", "value": {"doubleValue": span.cost_usd}})

    for k, v in span.metadata.items():
        attributes.append({"key": f"airun.metadata.{k}", "value": _format_otlp_attr_value(v)})

    # Status mapping: 0=UNSET, 1=OK, 2=ERROR
    status_code = 1
    status_msg = ""
    if span.status in (SpanStatus.FAILURE, SpanStatus.TIMEOUT):
        status_code = 2
        if span.error:
            status_msg = span.error.get("message", "Span execution failed")

    return {
        "traceId": trace_hex,
        "spanId": span_hex,
        "parentSpanId": parent_hex,
        "name": span.name,
        "kind": kind_int,
        "startTimeUnixNano": _to_unix_nano(span.start_time),
        "endTimeUnixNano": _to_unix_nano(span.end_time),
        "attributes": attributes,
        "status": {
            "code": status_code,
            "message": status_msg,
        },
    }


def export_trace_to_otel(
    trace_record: TraceRecord, service_name: str = "airun-ai-service"
) -> Dict[str, Any]:
    """Convert a TraceRecord to OpenTelemetry OTLP JSON format."""
    otlp_spans = [_span_to_otlp(s) for s in trace_record.spans]

    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": service_name}},
                        {"key": "telemetry.sdk.name", "value": {"stringValue": "airun"}},
                        {"key": "telemetry.sdk.version", "value": {"stringValue": "0.1.0"}},
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {
                            "name": "airun.tracer",
                            "version": "0.1.0",
                        },
                        "spans": otlp_spans,
                    }
                ],
            }
        ]
    }
