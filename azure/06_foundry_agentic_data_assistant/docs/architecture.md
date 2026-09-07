# Architecture

```text
User
  |
  v
agent/app.py
  |
  +--> Microsoft Foundry Prompt Agent
  |       |
  |       +--> Native Azure AI Search tool ---> policy index
  |       |
  |       +--> Function-call request (name + validated JSON arguments)
  |
  +--> agent/tools.py (client-side dispatcher; NO SQL)
          |
          +--> mock backend (first-success only)
          |
          +--> Azure Function HTTP API
                  |
                  +--> fixed stored procedure + bound parameters
                          |
                          v
                       Azure SQL
```

## Why this is safe

The model can choose a declared operation, but it cannot provide SQL text. The Function App is a second authorization/validation boundary. Azure SQL is a third boundary because the Function identity should receive only `EXECUTE` on the four approved read-only procedures.

## Supported structured tools

- `get_revenue_by_region(start_date, end_date)`
- `get_delayed_shipments(report_date)`
- `get_order_summary(order_id)`
- `get_metric_source(metric_name)`

## Search tool

The agent uses the Foundry Azure AI Search tool for policy/document retrieval. The index in this repo is intentionally small and keyword-based so the POC is easy to finish. If you already completed POC-05, point `SEARCH_INDEX_NAME` at that existing index instead.
