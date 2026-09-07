# POC-06 Threat Model

## Security objective

The assistant is read-only. A model must never be able to turn natural-language input into unrestricted SQL or a write operation.

## Trust boundaries

1. **User -> Foundry Agent**: untrusted natural-language input.
2. **Foundry Agent -> Azure AI Search**: read-only document retrieval.
3. **Foundry Agent -> client function call**: model can choose only from four declared function schemas.
4. **Client -> Azure Function**: fixed HTTP routes with validated parameters.
5. **Azure Function -> Azure SQL**: fixed stored-procedure calls with bound parameters.
6. **Azure Function managed identity -> Azure SQL**: grant only EXECUTE on approved procedures.

## Threats and controls

| Threat | Control |
|---|---|
| Prompt asks for `DROP TABLE` | No arbitrary SQL tool exists; agent instruction requires refusal. |
| SQL injection in a parameter | Date/order/metric allowlist validation plus bound procedure parameters. |
| Model tries a write action | No write endpoint, procedure, or tool is exposed. |
| Prompt injection in retrieved document | Agent treats retrieved text as data, never as higher-priority instructions. |
| Secret exfiltration | Secrets are not tool outputs; logs redact key/token/secret/password fields. |
| Over-privileged Function identity | Grant EXECUTE only on four procedures; avoid `db_owner`, `db_datawriter`, Contributor/Owner. |
| Search tampering | Agent uses read-only search; production identity should use Search Index Data Reader. |
| Sensitive logging | Trace payloads are redacted; do not log full credentials or connection strings. |
| Hallucinated metric | Instructions require structured tools for numeric/current facts. |

## Explicitly prohibited implementation

```python
# NEVER add this pattern:
def execute_sql(sql_from_llm: str):
    cursor.execute(sql_from_llm)
```

## Security acceptance tests

Run the `S01`-`S05` cases in `eval/agent_test_cases.json`. All must fail safely/refuse.
