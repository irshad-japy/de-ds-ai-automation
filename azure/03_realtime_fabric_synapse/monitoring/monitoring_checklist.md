# Monitoring and failure-recovery checklist

## 1. Event Hubs

Azure portal -> Event Hubs namespace / Event Hub -> Monitoring -> Metrics.

Capture:
- Incoming Messages
- Incoming Bytes
- Throttled Requests (should normally be zero in this tiny POC)
- Server Errors / User Errors if present

**Test**
Run:
`python producer/send_events.py --count 100 --delay 0.10`

Expected:
Incoming Messages rises shortly afterward.

## 2. Databricks Structured Streaming

Check the running stream / Spark UI / notebook output.

Capture:
- input rows per second;
- processed rows per second;
- batch duration;
- query status;
- checkpoint path.

### Restart test

1. Let Silver process some events.
2. Record Silver row count and distinct event_id count.
3. Stop the streaming notebook/query.
4. Send 20 more events.
5. Restart using the SAME checkpoint path.
6. Recount.

Expected:
- Spark resumes from checkpointed offsets.
- already-processed Kafka/Event Hubs offsets are not re-read as new work;
- Silver remains deduplicated by event_id within the configured watermark/state behavior.

Never delete the checkpoint and then call it a "restart test"; deleting it changes the semantics.

## 3. Fabric Eventstream / Eventhouse

Check:
- source status;
- destination status;
- live data preview after publish;
- Eventhouse ingestion/query freshness.

Run:
`ShipmentEvents | summarize latest=max(event_ts), rows=count()`

## 4. Data freshness

KQL:
`ShipmentEvents | summarize latest=max(event_ts)`

Compare with current UTC time.

Also inspect Gold `last_event_ts`.

## 5. Pipeline/transform failures

If you create a Fabric Pipeline/Dataflow/Notebook:
- record one successful run;
- intentionally cause one harmless failure, such as a wrong temporary path;
- capture the failure message;
- fix it;
- rerun successfully.

This satisfies the POC requirement that one failure path is captured and recovered.

## 6. Azure Monitor / Log Analytics

If you already have a Log Analytics workspace and diagnostic settings are practical:
- enable diagnostic logs for the smallest required scope;
- avoid turning on every category for a learning POC;
- document the destination and retention.

If not practical, record the exact production design and mark it "not deployed in POC".
