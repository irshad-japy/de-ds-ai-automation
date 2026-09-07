# Troubleshooting

## `az` is not recognized

Azure CLI is a separate application; the Python package `azure-identity` does not install it. Install Azure CLI, close/reopen the terminal, then run:

```bash
az --version
az login
```

## `DefaultAzureCredential` authentication failed

Run `az login`, verify the active subscription with `az account show`, and confirm you have access to the Foundry project.

## Foundry 401/403

Check your project endpoint and RBAC. For normal agent use, grant the appropriate Foundry User role rather than Azure Owner/Contributor simply to make the demo work.

## Search tool 401/403

Check the Foundry connected resource and its authentication. For Microsoft Entra/RBAC, the project/resource managed identity needs appropriate Search read permissions. Do not grant write roles when the assistant only reads.

## Search returns no citation

Ensure the agent instruction explicitly requests citations and that the index contains `title` and `url` fields. Verify the index directly with `python -m search.verify_search`.

## `func` is not recognized

Install Azure Functions Core Tools v4 and reopen the terminal.

## `pyodbc.InterfaceError` / ODBC driver missing

Install Microsoft ODBC Driver 18 for SQL Server on your local machine. In Azure, inspect available drivers or use a supported Functions hosting image/plan. The expected driver name is set by `AZURE_SQL_ODBC_DRIVER`.

## Azure SQL login failed for Function identity

1. Confirm Function App -> Identity -> System assigned = On.
2. Confirm an Azure SQL Microsoft Entra administrator is configured.
3. Run `sql/03_grant_function_identity.sql` with the exact Function identity name.
4. Confirm only the four `GRANT EXECUTE` statements are present.
5. Restart the Function App after changing identity/app settings.

## Function endpoint returns 401

`health` is anonymous, but business routes use Function authorization. Put the Function key in local `.env` as `FUNCTION_KEY`; never commit it.

## Agent calls wrong tool

Make the question unambiguous first. Then inspect `logs/agent_trace.jsonl`. If the wrong tool is consistently selected, strengthen descriptions in `agent/tool_schemas.py` and `agent/instructions.md`, then create a new agent version.

## Evaluation reports search tool missing

The SDK's response-item name for hosted search events can vary. The app detects any response item whose type contains `search`. Confirm the actual response trace and adjust `_trace_response_items()` if a future SDK changes the event name.
