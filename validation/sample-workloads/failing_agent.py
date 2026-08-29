"""Sample Workload: Failing Workflow to observe error propagation and wasted cost."""

import time

from airun import SpanKind, trace


@trace(kind=SpanKind.LLM, model="gpt-4o", provider="openai")
def preliminary_planning(task: str) -> str:
    time.sleep(0.06)
    return "Plan step 1: Query internal warehouse database"


@trace(kind=SpanKind.DB, provider="warehouse_postgres")
def query_warehouse_db():
    time.sleep(0.04)
    raise ConnectionRefusedError("Database port 5432 unreachable (Connection refused)")


def main():
    try:
        with trace("failing_data_pipeline", kind=SpanKind.WORKFLOW):
            plan = preliminary_planning("Sync customer records")
            print(f"Plan: {plan}")
            query_warehouse_db()
    except Exception as e:
        print(f"\nCaught expected exception: {e}")
        print("Inspect wasted cost and failure trace: airun report latest\n")


if __name__ == "__main__":
    main()
