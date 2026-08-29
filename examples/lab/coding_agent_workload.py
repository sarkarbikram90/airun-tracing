"""Workload Archetype 4: Coding & Debugging Loop Agent (Read -> Edit -> Test -> Fix)."""

from __future__ import annotations

import time

from airun import SpanKind, SpanStatus, set_span_metadata, set_span_tokens, trace


@trace(kind=SpanKind.TOOL, provider="filesystem")
def read_source_file(file_path: str) -> str:
    time.sleep(0.03)
    set_span_metadata({"path": file_path, "bytes": 1024})
    return (
        "def calculate_discount(price, pct):\n    return price - pct # BUG: should be price * pct"
    )


@trace(kind=SpanKind.LLM, model="claude-3-5-sonnet", provider="anthropic")
def generate_code_patch(code: str, error_context: str) -> str:
    time.sleep(0.12)
    set_span_tokens(input_tokens=1800, output_tokens=220)
    return "def calculate_discount(price, pct):\n    return price * (1.0 - pct)"


@trace(kind=SpanKind.TOOL, provider="pytest_runner")
def run_test_suite(attempt: int) -> dict:
    time.sleep(0.05)
    if attempt == 1:
        # First test run fails
        set_span_metadata({"status": "failed", "failures": 1})
        return {"passed": False, "error": "AssertionError: expected 80.0, got -19"}
    # Second test run passes
    set_span_metadata({"status": "passed", "tests": 5})
    return {"passed": True, "error": None}


def run_coding_agent():
    with trace("coding_debugger_workflow", kind=SpanKind.WORKFLOW) as root:
        # 1. Read file
        code = read_source_file("pricing_calc.py")

        # 2. Run initial test (fails)
        with trace("initial_test_run", kind=SpanKind.AGENT_STEP) as step_test:
            res1 = run_test_suite(attempt=1)
            if not res1["passed"]:
                step_test.status = SpanStatus.FAILURE
                step_test.error = {"type": "TestFailure", "message": res1["error"]}

        # 3. Model generates patch
        patch = generate_code_patch(code, res1["error"])

        # 4. Re-run test with patch (passes)
        with trace("verification_test_run", kind=SpanKind.AGENT_STEP):
            res2 = run_test_suite(attempt=2)

        print(
            f"[coding_agent_workload] Fixed bug: {patch[:30]}... Test Passed: {res2['passed']} (Trace ID: {root.trace_id[:8]})"
        )


if __name__ == "__main__":
    run_coding_agent()
