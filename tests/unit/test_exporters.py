"""Unit tests for JSON and OpenTelemetry exporters."""

import json

from airun.events.models import TraceRecord
from airun.exporters.json_export import export_trace_to_json
from airun.exporters.otel_export import export_trace_to_otel


def test_export_trace_to_json(simple_success_trace: TraceRecord):
    json_str = export_trace_to_json(simple_success_trace)
    parsed = json.loads(json_str)
    assert parsed["trace_id"] == simple_success_trace.trace_id
    assert "summary" in parsed
    assert "spans" in parsed
    assert len(parsed["spans"]) == len(simple_success_trace.spans)


def test_export_trace_to_otel(simple_success_trace: TraceRecord):
    otel_data = export_trace_to_otel(simple_success_trace, service_name="test-service")
    assert "resourceSpans" in otel_data
    res_spans = otel_data["resourceSpans"][0]
    scope_spans = res_spans["scopeSpans"][0]
    spans = scope_spans["spans"]

    assert len(spans) == len(simple_success_trace.spans)
    root_span = spans[0]
    assert root_span["name"] == "simple_workflow"
    assert "traceId" in root_span
    assert "spanId" in root_span
    assert "attributes" in root_span
    assert root_span["status"]["code"] == 1  # STATUS_CODE_OK

    # Check child LLM span
    llm_span = spans[1]
    assert llm_span["name"] == "llm_planning"
    assert llm_span["parentSpanId"] == root_span["spanId"]
    assert llm_span["kind"] == 3  # SPAN_KIND_CLIENT

    # Verify OpenTelemetry GenAI semantic attributes
    attr_map = {attr["key"]: attr["value"] for attr in llm_span["attributes"]}
    assert "gen_ai.system" in attr_map
    assert "gen_ai.request.model" in attr_map
    assert attr_map["gen_ai.request.model"]["stringValue"] == "gpt-4o-mini"
    assert "gen_ai.usage.input_tokens" in attr_map
    assert str(attr_map["gen_ai.usage.input_tokens"]["intValue"]) == "1000"
    assert "gen_ai.usage.output_tokens" in attr_map
    assert str(attr_map["gen_ai.usage.output_tokens"]["intValue"]) == "500"
    assert "airun.cost_usd" in attr_map
