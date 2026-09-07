# Troubleshooting

## `az is not recognized`

Azure CLI is optional for the manual portal path in this project.
The local Event Hubs Python producer does not require `az` when using a connection string.

If you later use `DefaultAzureCredential`, managed identity, or CLI-based login,
install Azure CLI separately and run `az login`.

## Python: `ModuleNotFoundError: azure.eventhub`

Activate the venv and install requirements:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
```

## Event Hubs sender says connection string missing

Check `.env` exists in the project root and contains:
- `EVENT_HUB_CONNECTION_STRING`
- `EVENT_HUB_NAME`

Do not wrap the connection string across multiple lines.

## Receiver prints nothing

Possible causes:
- producer has not sent events;
- starting position is `@latest` and no new events arrive;
- wrong Event Hub name;
- wrong namespace/connection string;
- network/firewall issue;
- consumer group behavior.

Try:
```bat
python producer\receive_events.py --max-events 10 --starting-position -1
```

## Databricks Kafka authentication error

Check:
- namespace name;
- port `9093`;
- SASL mechanism `PLAIN`;
- protocol `SASL_SSL`;
- full Event Hubs connection string stored in the Databricks secret;
- Event Hub name/subscription;
- policy has Listen rights.

## `dropDuplicatesWithinWatermark` not found

Your runtime may expose an older Spark API.

Replace:
```python
.withWatermark("event_ts", "10 minutes").dropDuplicatesWithinWatermark(["event_id"])
```

with:
```python
.withWatermark("event_ts", "10 minutes").dropDuplicates(["event_id"])
```

Then document the runtime difference in your POC notes.

## Databricks cannot write to ABFSS

This is an ADLS authentication/authorization issue, not a Spark transformation issue.

Verify:
- storage access configuration;
- RBAC role assignment;
- filesystem/container name;
- storage account name;
- Unity Catalog external location/credential if used.

## Synapse OPENROWSET access denied

Your serverless SQL identity needs access to the storage path, or your environment
must be configured with the appropriate credential.

Also verify:
- correct `dfs.core.windows.net` path;
- files actually exist;
- signed-in identity is the identity you granted access to.

## Fabric Eventstream shows no data

Check in order:
1. Python producer is sending.
2. Azure Event Hubs Incoming Messages > 0.
3. Fabric source points to the correct namespace + Event Hub.
4. Connection auth is valid.
5. Eventstream changes were **published**.
6. Source/destination is not paused.
7. Destination table mapping is correct.

## KQL `ShipmentEvents` empty

If Eventstream source is healthy but destination is empty:
- validate table column types;
- validate mapping;
- temporarily use preview;
- inspect destination errors;
- create a fresh small test event.

## Semantic totals do not match

Common reason: raw Eventhouse data intentionally contains duplicates while
Databricks Silver deduplicates by `event_id`.

Choose and document the authoritative layer:
- Eventhouse = raw real-time operational analytics;
- Silver/Gold = deduplicated curated analytics.

If the semantic model is supposed to match Gold, build it from Gold/curated data.
