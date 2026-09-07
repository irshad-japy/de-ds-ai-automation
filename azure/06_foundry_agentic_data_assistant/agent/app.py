from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

from agent.tools import TOOL_DISPATCH
from agent.trace import configure_logging, write_trace

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
configure_logging()


def _item_type(item: Any) -> str:
    return str(getattr(item, "type", item.__class__.__name__))


def _trace_response_items(response: Any, tool_trace: list[str]) -> None:
    for item in getattr(response, "output", []) or []:
        item_type = _item_type(item)
        if "search" in item_type.lower():
            tool_trace.append("azure_ai_search")
            write_trace("tool_selected", {"tool": "azure_ai_search", "response_item_type": item_type})


def ask_agent(question: str, max_rounds: int = 8) -> dict[str, Any]:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.getenv("FOUNDRY_AGENT_NAME", "Foundry-Agentic-Data-Assistant")
    agent_version = os.getenv("FOUNDRY_AGENT_VERSION", "2")

    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai = project.get_openai_client()
    tool_trace: list[str] = []
    started = time.perf_counter()

    write_trace("question", {"question": question, "agent_name": agent_name})

    agent_ref = {
        "agent_reference": {
            "name": agent_name,
            "version": agent_version,
            "type": "agent_reference",
        }
    }

    response = openai.responses.create(
        input=[{"role": "user", "content": question}],
        extra_body=agent_ref,
    )
    _trace_response_items(response, tool_trace)

    for _ in range(max_rounds):
        function_outputs: ResponseInputParam = []
        function_called = False

        for item in getattr(response, "output", []) or []:
            if _item_type(item) != "function_call":
                continue
            function_called = True
            name = item.name
            arguments = json.loads(item.arguments or "{}")
            tool_trace.append(name)
            write_trace("tool_selected", {"tool": name, "arguments": arguments})

            if name not in TOOL_DISPATCH:
                result = {"error": f"Tool {name} is not implemented."}
            else:
                tool_start = time.perf_counter()
                try:
                    result = TOOL_DISPATCH[name](**arguments)
                    write_trace(
                        "tool_result",
                        {"tool": name, "latency_ms": round((time.perf_counter() - tool_start) * 1000, 2), "result": result},
                    )
                except Exception as exc:
                    result = {"error": type(exc).__name__, "message": str(exc)}
                    write_trace("tool_failure", {"tool": name, "error": type(exc).__name__, "message": str(exc)})

            function_outputs.append(
                FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps(result, default=str),
                )
            )

        if not function_called:
            break

        response = openai.responses.create(
            input=function_outputs,
            extra_body=agent_ref,
        )
        _trace_response_items(response, tool_trace)

    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    answer = response.output_text or ""
    write_trace("final_answer", {"latency_ms": latency_ms, "tools": tool_trace, "answer": answer})
    return {"question": question, "answer": answer, "tools": tool_trace, "latency_ms": latency_ms}


def main() -> None:
    print("POC-06 Agentic Data Assistant")
    print("Type 'exit' to quit.\n")
    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        result = ask_agent(question)
        print(f"\nAgent: {result['answer']}")
        print(f"Tool trace: {result['tools']}")
        print(f"Latency: {result['latency_ms']} ms\n")


if __name__ == "__main__":
    main()