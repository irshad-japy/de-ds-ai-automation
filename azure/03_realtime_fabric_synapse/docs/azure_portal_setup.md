# Azure portal setup — step by step

This guide assumes you are new to Azure.

## Resource naming used in examples

Use globally unique names where required.

- Resource group: `rg-poc03-realtime-dev`
- Event Hubs namespace: `ehns-poc03-<unique>`
- Event Hub: `shipment-events`
- Storage account: `stpoc03<unique>`
- ADLS container/filesystem: `realtime`
- Databricks workspace: `dbw-poc03-realtime`
- Synapse workspace: `syn-poc03-<unique>`
- Fabric workspace: `poc03-realtime-fabric`

Use one Azure region where possible.

---

## STEP 1 — Create resource group

1. Azure portal -> search **Resource groups**.
2. Select **Create**.
3. Subscription: your subscription.
4. Resource group: `rg-poc03-realtime-dev`.
5. Region: choose a nearby region supported by the services you need.
6. Review + create -> Create.

### Verify
Open the resource group. It should exist and initially be empty.

---

## STEP 2 — Create ADLS Gen2 storage

1. Search **Storage accounts** -> Create.
2. Resource group: `rg-poc03-realtime-dev`.
3. Name: `stpoc03<unique>`.
4. Performance: Standard.
5. Redundancy: choose the least expensive option acceptable for your learning account.
6. In Advanced settings, enable **Hierarchical namespace**.
7. Create.

After deployment:
1. Open the storage account.
2. Data storage -> Containers.
3. Create container/filesystem `realtime`.

The code uses these paths:
- `delta/bronze/shipment_events`
- `delta/silver/shipment_events`
- `gold/shipment_summary`
- `checkpoints/...`

Spark creates subfolders automatically after permissions are correct.

### Verify
`realtime` exists.

---

## STEP 3 — Create Event Hubs namespace

1. Search **Event Hubs**.
2. Create namespace.
3. Resource group: `rg-poc03-realtime-dev`.
4. Namespace: `ehns-poc03-<unique>`.
5. Tier: choose the smallest tier that supports the features you use.
6. Keep throughput/capacity minimal for this POC.
7. Create.

### Create the Event Hub

1. Open the namespace.
2. Event Hubs -> **+ Event Hub**.
3. Name: `shipment-events`.
4. Partition count: a small count is enough for learning.
5. Message retention: keep minimal/default appropriate for POC.
6. Create.

### Beginner authentication for this POC

For the quickest learning path, create/use a Shared Access Policy that can Send/Listen.
For production, prefer Microsoft Entra ID / managed identity where supported.

1. Namespace -> Shared access policies.
2. Create a POC policy, for example `poc03-send-listen`.
3. Enable only the rights needed (Send and Listen for this combined learning policy).
4. Copy the primary connection string to your local `.env`.
5. NEVER commit it.

### Verify
Event Hub `shipment-events` exists.

---

## STEP 4 — Test Event Hubs with local Python BEFORE Databricks/Fabric

From project root on Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set:
- `EVENT_HUB_CONNECTION_STRING`
- `EVENT_HUB_NAME=shipment-events`

Send:
```bat
python producer\send_events.py --count 20 --delay 0.2
```

Receive:
```bat
python producer\receive_events.py --max-events 10 --starting-position -1
```

### Verify
- sender prints 20 successful attempts;
- receiver prints JSON events;
- Event Hubs metric **Incoming Messages** increases.

Do not continue until this works.

---

## STEP 5 — Create Azure Databricks workspace

1. Search **Azure Databricks** -> Create.
2. Resource group: `rg-poc03-realtime-dev`.
3. Workspace: `dbw-poc03-realtime`.
4. Pricing tier: choose the lowest practical option for your account/region that supports your POC.
5. Create.
6. Launch workspace.

### Create small compute

Use the smallest practical single-user/single-node or minimal cluster/serverless configuration available in your workspace.

Important:
- Avoid large worker counts.
- Stop/terminate compute immediately after tests.
- Enable auto-termination if available.

### Give Databricks access to ADLS

Preferred enterprise approach:
- managed identity/service principal/access connector + RBAC/Unity Catalog/external location.

For a beginner POC, use the access pattern supported by your workspace and account,
but do NOT embed storage account keys in committed notebooks.

At minimum Databricks must be able to read/write the `realtime` filesystem.

### Add Event Hubs secret

Create a Databricks secret scope named `poc03`, then store:
- key: `event-hub-connection-string`
- value: the real Event Hubs connection string

Do not paste the value into the notebook source.

### Run notebooks/scripts

Import/copy:
1. `databricks/stream_to_delta.py`
2. `databricks/inspect_and_validate.py`
3. `databricks/export_gold_parquet.py`

Edit placeholder namespace/storage account values.

Start `stream_to_delta.py`, then locally run:
```bat
python producer\send_events.py --count 200 --delay 0.15
```

### Verify Databricks
Run `inspect_and_validate.py`.

Expected:
- Silver rows > 0
- Silver row count == distinct `event_id`
- group counts display
- late/duplicate behavior is visible in the experiment

Then run `export_gold_parquet.py`.

Expected:
- Parquet files appear under:
  `realtime/gold/shipment_summary`

---

## STEP 6 — Create Synapse workspace for serverless SQL

You are using only the built-in **serverless SQL** path for this POC.
Do NOT create a dedicated SQL pool.

1. Search **Azure Synapse Analytics** -> Create workspace.
2. Resource group: `rg-poc03-realtime-dev`.
3. Workspace name: `syn-poc03-<unique>`.
4. Configure the required ADLS Gen2 workspace storage/filesystem as prompted.
   You may use a separate minimal filesystem if Synapse requires one.
5. Create.
6. Open Synapse Studio.

### Query Gold Parquet

Open:
- Data / Develop -> new SQL script
- connect to the built-in serverless SQL pool

Paste `synapse/serverless_queries.sql`.
Replace `<storage-account>`.

Your signed-in identity needs read access to the `realtime/gold` path.

### Verify
- `SELECT TOP 100` returns Gold rows.
- aggregate totals are non-null.
- record data processed/scanned from query details.
- compare broad vs narrow-column query as a cost lesson.

---

## STEP 7 — Fabric

Follow `fabric/setup_notes.md`.

Minimum success:
- Fabric workspace exists;
- Eventhouse/KQL database exists;
- Eventstream reads Azure Event Hubs;
- Eventstream destination writes to `ShipmentEvents`;
- KQL queries return data;
- Lakehouse exists;
- Gold data is accessible by shortcut where practical, otherwise tiny copy is documented;
- a small semantic model/report is produced.

---

## STEP 8 — Monitoring and governance

Follow:
- `monitoring/monitoring_checklist.md`
- `governance/purview_notes.md`

For optional/cost-sensitive services, document a production design if you cannot safely deploy them.

---

## STEP 9 — Cleanup

Use `docs/cleanup.md`.

For this POC, the most important immediate cleanup actions are:
- stop Databricks compute;
- stop/delete optional Fabric trial items/capacity if you no longer need them;
- delete the Azure resource group after evidence is captured.
