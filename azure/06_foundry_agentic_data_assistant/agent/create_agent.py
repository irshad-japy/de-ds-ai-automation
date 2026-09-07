from __future__ import annotations

import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AISearchIndexResource,
    AzureAISearchQueryType,
    AzureAISearchTool,
    AzureAISearchToolResource,
    PromptAgentDefinition,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from agent.tool_schemas import build_function_tools

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def build_agent_tools(project: AIProjectClient):
    tools = list(build_function_tools())
    search_connection_name = os.getenv("SEARCH_CONNECTION_NAME", "").strip()
    search_index_name = os.getenv("SEARCH_INDEX_NAME", "").strip()

    if search_connection_name and search_index_name:
        connection = project.connections.get(search_connection_name)
        tools.append(
            AzureAISearchTool(
                azure_ai_search=AzureAISearchToolResource(
                    indexes=[
                        AISearchIndexResource(
                            project_connection_id=connection.id,
                            index_name=search_index_name,
                            query_type=AzureAISearchQueryType.SIMPLE,
                        )
                    ]
                )
            )
        )
    else:
        print("[WARN] SEARCH_CONNECTION_NAME/SEARCH_INDEX_NAME not set; creating functions-only agent.")
    return tools


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"]
    agent_name = os.getenv("FOUNDRY_AGENT_NAME", "poc06-agentic-data-assistant")
    instructions = (ROOT / "agent" / "instructions.md").read_text(encoding="utf-8")

    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    tools = build_agent_tools(project)
    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(model=model, instructions=instructions, tools=tools),
        description="POC-06 read-only agentic data assistant",
    )
    print(f"[SUCCESS] Agent version created: name={agent.name} version={agent.version} id={agent.id}")
    print("Next: python -m agent.app")


if __name__ == "__main__":
    main()
