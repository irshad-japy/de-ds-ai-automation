The file content provided contains the compressed binary stream and file directory table of poc06_foundry_agentic_data_assistant.zip, rather than the rendered plaintext of README.md.

Based on the repository structure (agent/create_agent.py, agent/smoke_test.py, agent/app.py, eval/run_evaluation.py), Step 14 typically completes the local script verifications (scripts/test_tools_local.py) or deploys the agent definition. Step 15 in this architecture almost always corresponds to either creating/registering the agent in Azure AI Foundry or running the agent interactive app / smoke test.

Here are the step-by-step guides for the two primary paths at Step 15.

Path A: Registering the Agent in Azure AI Foundry (agent/create_agent.py or Portal)
If Step 14 verified your tools and Step 15 requires registering the agent with Azure AI Foundry:

Option 1: Via the Terminal (Automated)
Open your terminal in the root directory: poc06_foundry_agentic_data_assistant.

Check your .env file to ensure these values are set:

PROJECT_CONNECTION_STRING (from your Azure AI Foundry Project Overview)

AZURE_OPENAI_DEPLOYMENT_NAME (e.g., gpt-4o or gpt-4)

AZURE_AI_SEARCH_ENDPOINT and AZURE_AI_SEARCH_KEY

AZURE_FUNCTION_URL and AZURE_FUNCTION_KEY

Run the agent creation script:

Bash
python agent/create_agent.py
Inspect the output: Look for a line returning Agent ID: asst_.... Copy this ID and paste it into your .env file under AZURE_AI_AGENT_ID.

Option 2: Via the Azure AI Foundry Portal (Manual UI)
Navigate to ai.azure.com and sign in.

Under Project, select your active project workspace.

In the left-hand navigation pane, click Build > Agents (or Assistants).

Click + Create Agent (or + New Assistant) in the top bar.

In the configuration panel on the right:

Name: Enter Foundry-Agentic-Data-Assistant.

Deployment / Model: Select your deployed model (e.g., gpt-4o).

Instructions: Open agent/instructions.md on your computer, copy the full text, and paste it into the Instructions text box.

Under Tools:

If using custom function calling via Python, the tools are loaded through agent/tools.py via the SDK.

If connecting Search directly in the portal, click + Add tool > Azure AI Search, select your search resource, and point it to the index created by search/setup_search_index.py.

Click Save in the top-right corner.

Path B: Running the Smoke Test or Interactive App (agent/smoke_test.py or agent/app.py)
If Step 14 created the agent and Step 15 is launching the interface or smoke testing:

1. Running the Smoke Test
Ensure your .env file contains your active AZURE_AI_AGENT_ID.

In your terminal, run:

Bash
python agent/smoke_test.py
What to look for on screen:

The script will initialize a thread in Azure AI Foundry.

It sends a test query (e.g., querying policy data or SQL read-only procedures).

You should see status messages transitioning from queued → in_progress → completed.

The output will print the final assistant response along with tool execution logs.

2. Running the Front-End / Web Interface
If Step 15 is launching the application:

Check whether agent/app.py uses Streamlit or standard Python by inspecting the top imports.

If it is a Streamlit app, run:

Bash
streamlit run agent/app.py
If it is a standard FastAPI / script, run:

Bash
python agent/app.py
Open your browser to the local URL displayed in the terminal (typically http://localhost:8501 for Streamlit or http://localhost:8000 for FastAPI).

What is the exact heading or title of Step 15 in your README.md, and what error message is appearing in your terminal?

