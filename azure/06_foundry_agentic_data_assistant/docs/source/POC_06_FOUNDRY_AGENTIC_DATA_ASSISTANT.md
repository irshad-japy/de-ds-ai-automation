# POC-06 — Agentic Data Assistant with Microsoft Foundry Agent Service

## Objective

Build a read-only data assistant that can choose between structured-data and document-retrieval tools.

## Architecture

```text
User question
   |
   v
Foundry Agent
   |
   +--> Tool 1: Azure AI Search knowledge retrieval
   |
   +--> Tool 2: read-only Azure SQL/Synapse query API
   |
   +--> Tool 3: business metric function
   |
   v
Answer + tool trace + citations
```

## Key rule

The agent must **not** receive unrestricted SQL execution or write permissions.

## Services

- Microsoft Foundry Agent Service
- Azure AI Search
- Azure SQL or Synapse serverless
- Azure Functions
- Managed Identity/RBAC
- Application Insights / Foundry tracing/evaluation

## Steps

### 1. Define supported questions

Examples:

- “What was revenue by region?”
- “Which policy explains return eligibility?”
- “How many delayed shipments occurred yesterday?”
- “What is the source of this metric?”

### 2. Build a read-only structured data tool

Do not expose arbitrary `execute_sql(sql_from_llm)`.

Instead expose safe functions such as:

```text
get_revenue_by_region(start_date, end_date)
get_delayed_shipments(date)
get_order_summary(order_id)
```

Validate every argument.

### 3. Build a knowledge tool

Reuse POC-05 Azure AI Search.

### 4. Create the Foundry agent

Instructions should include:

- use tools for factual questions;
- never invent unavailable values;
- cite sources;
- distinguish structured metric results from policy documents;
- never perform writes/deletes.

### 5. Test tool selection

Create a table:

| Question | Expected tool |
|---|---|
| What is our return policy? | search |
| Revenue by region? | structured metric |
| Why is order 1001 delayed? | structured + search if needed |

### 6. Add authorization boundaries

Use a dedicated read-only identity or function API layer.

Do not assign owner/contributor privileges to the agent runtime just to make the demo easy.

### 7. Add tracing

Capture:

- selected tool
- tool arguments
- response latency
- failures
- final answer

Redact sensitive data in logs.

### 8. Evaluate

Create 15 deterministic test questions.

Metrics:

```text
correct_tool
correct_answer
citation_present
unsafe_action_refused
latency
```

### 9. Security tests

Ask the agent to:

- delete an order;
- expose secrets;
- execute arbitrary SQL;
- ignore previous instructions.

Expected result: refuse or remain constrained by tool design.

## Validation

- Agent uses the right tool for most test questions.
- Tool layer is read-only.
- No SQL text from the model reaches the database directly.
- Traces show tool choices.
- Unsupported action attempts fail safely.

## GitHub artifacts

```text
agent/
  instructions.md
  tools.py
  app.py
eval/
  agent_test_cases.json
  evaluation_results.md
security/
  threat_model.md
```

## Interview questions

1. RAG vs agent?
2. Why are tools safer than arbitrary SQL?
3. How do you authorize an agent?
4. What should be logged in an agent trace?
5. How do you evaluate tool selection?
6. How would you prevent prompt injection from retrieved content?

## CV text — USE ONLY AFTER COMPLETION

- Built a Microsoft Foundry agentic data assistant that routes questions between Azure AI Search knowledge retrieval and read-only analytical tools.
- Implemented constrained tool schemas, Managed Identity/RBAC boundaries, citations and trace-based evaluation rather than unrestricted LLM-generated SQL.
- Tested prompt-injection, secret-exposure and write-operation scenarios with explicit safe-failure behavior.
