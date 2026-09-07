# POC-03 — Real-Time Data Platform with Event Hubs, Fabric and Synapse

## Objective

Practice both the Azure streaming stack in the CV and newer Microsoft Fabric real-time capabilities.

## Architecture

```text
Python synthetic event producer
        |
        v
Azure Event Hubs
        |
        +--> Databricks Structured Streaming --> Delta/ADLS
        |
        +--> Fabric Eventstream --> Eventhouse/KQL
                                  |
                                  +--> Real-Time dashboard / alerts
Delta Gold
   |
   +--> Synapse serverless SQL
   +--> Fabric OneLake/Lakehouse/Warehouse
   +--> Semantic Model
```

## Services

- Azure Event Hubs
- Azure Databricks Structured Streaming
- ADLS Gen2 / Delta
- Microsoft Fabric
- OneLake
- Lakehouse
- Warehouse
- Notebooks
- Dataflows Gen2 / Pipelines
- Fabric Real-Time Intelligence
- Eventstream / Eventhouse / KQL
- Synapse serverless SQL
- Semantic Model
- Microsoft Purview
- Azure Monitor / Log Analytics

## Cost guardrails

- One small Event Hub and minimal throughput.
- Send only a few hundred events.
- Stop Databricks compute.
- Use Fabric trial if available.
- Use Synapse serverless only for tiny files and select required columns.
- Do not create Synapse dedicated SQL pools.

## Steps

### 1. Create an event schema

```json
{
  "event_id": "evt-001",
  "order_id": 1001,
  "event_type": "SHIPPED",
  "event_ts": "2026-08-28T10:00:00Z",
  "region": "IN-SOUTH"
}
```

### 2. Create Event Hubs namespace + event hub

Use the smallest suitable tier for a learning POC.

Store connection details outside Git. Prefer identity-based auth where supported by your chosen producer/consumer setup.

### 3. Produce synthetic events

Create a Python producer that sends 100–500 events with a small delay.

Commit the code with environment-variable placeholders only.

### 4. Databricks streaming path

Read from Event Hubs, parse JSON, apply a watermark/dedup rule, and write Delta.

Demonstrate:

- checkpointing
- late event handling
- duplicate event handling
- restart behavior

### 5. Fabric trial path

If using a personal email, follow Microsoft's current Fabric personal-account/trial onboarding process.

Create:

- workspace
- Lakehouse
- optional Warehouse

Load or shortcut a curated dataset into OneLake.

### 6. Real-Time Intelligence path

Create:

- Eventstream
- Eventhouse
- KQL database/table

Route a sample stream and query it with KQL.

Starter KQL ideas:

```kusto
ShipmentEvents
| summarize events=count() by bin(event_ts, 5m), event_type
```

```kusto
ShipmentEvents
| where event_type == "DELAYED"
| summarize delayed=count() by region
```

### 7. OneLake shortcut

Create a shortcut where practical so the POC demonstrates access without unnecessary copying.

### 8. Synapse serverless serving

Create an external/serverless query over curated Parquet/Delta-compatible data supported by your setup.

Measure data scanned and document why selecting fewer columns matters for cost.

### 9. Fabric transformation

Use at least one of:

- Fabric Notebook
- Dataflow Gen2
- Pipeline

Create a small curated table.

### 10. Semantic Model

Create a minimal semantic model with:

- total orders
- revenue
- delayed shipments
- average fulfillment time

### 11. Purview/governance

If Purview is practical within budget/account availability:

- register relevant sources;
- scan only a tiny scope;
- review lineage/classification.

If it is not practical, document the exact enterprise design and do not pretend it was deployed.

### 12. Monitoring

Capture:

- Event Hub incoming message metric
- stream processing status
- Eventstream/Eventhouse metrics if available
- pipeline failures
- data freshness

## Validation

- Events arrive.
- Restart does not duplicate already-processed events.
- KQL returns expected grouped counts.
- Synapse serverless can query curated data.
- Semantic model produces correct totals.
- One failure path is captured and recovered.

## GitHub artifacts

```text
producer/
  send_events.py
databricks/
  stream_to_delta.py
fabric/
  setup_notes.md
kql/
  shipment_queries.kql
synapse/
  serverless_queries.sql
governance/
  purview_notes.md
```

## Interview questions

1. Event Hubs partition key trade-offs?
2. What is a watermark in streaming?
3. Checkpoint vs watermark?
4. Eventhouse/KQL vs lakehouse?
5. When use Synapse serverless?
6. OneLake shortcut vs copy?
7. How would you monitor event freshness?
8. How does Purview complement Unity Catalog?

## CV text — USE ONLY AFTER COMPLETION

- Built a near-real-time Azure data pipeline using Event Hubs, structured streaming and Delta Lake with checkpointing, watermarks and deduplication.
- Explored Microsoft Fabric Real-Time Intelligence using Eventstream, Eventhouse and KQL for low-latency event analysis.
- Published curated data through OneLake/Fabric and Synapse serverless patterns with semantic modeling and cost-aware querying.
- Added governance and observability notes covering Purview, lineage, data freshness and streaming health.
