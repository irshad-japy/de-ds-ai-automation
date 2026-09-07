# Azure Functions option

For the minimal capstone you do not need a Function if Event Hubs Capture or a direct consumer already writes events to storage. The included `function_app.py` shows an optional Event Hubs-triggered Python v2 Function that validates events and emits accepted JSON to a Blob output binding.

Install the optional dependency locally with:

```powershell
poetry install --with functions
```

When deploying, keep connection settings in Function App configuration / Key Vault references, not in source control.
