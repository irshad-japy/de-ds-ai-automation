# Agent integration

There are two safe paths:

1. `assistant.py` — application-owned, constrained read-only assistant. It exposes only knowledge retrieval and Gold metrics, so it is ideal for the capstone demo.
2. `foundry_agent_runner.py` — connects to an agent you already created in Microsoft Foundry by setting `FOUNDRY_AGENT_NAME`.

Recommended agent test questions:

```powershell
poetry run python -m ai.agent.assistant --mode policy "What is the return window for opened electronics?"
poetry run python -m ai.agent.assistant --mode metric "What is total revenue?"
poetry run python -m ai.agent.assistant --mode mixed "What is total revenue and when should support notify a customer about shipment delay?"
```

The application code never provides write tools to the model.
