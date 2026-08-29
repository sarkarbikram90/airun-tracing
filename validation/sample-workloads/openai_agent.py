"""Sample Workload: Real or Mocked OpenAI Client Auto-Instrumentation."""

import os

from airun import SpanKind, trace
from airun.sdk.wrappers import wrap_openai_client


def run_openai_sample():
    try:
        from openai import OpenAI

        api_key = os.environ.get("OPENAI_API_KEY", "sk-mock-key-for-testing")
        client = OpenAI(api_key=api_key)
        client = wrap_openai_client(client)

        with trace("openai_agent_workflow", kind=SpanKind.WORKFLOW) as root:
            # If real key is provided, this executes against OpenAI API; otherwise handles fallback
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": "Explain AI execution profiling in 10 words."}
                    ],
                )
                print(f"OpenAI Response: {response.choices[0].message.content}")
            except Exception as e:
                print(f"API call simulated or failed safely: {e}")
            print(f"Trace ID: {root.trace_id[:8]}")
    except ImportError:
        print("openai package not installed. Run 'pip install openai' to test live API calls.")


if __name__ == "__main__":
    run_openai_sample()
