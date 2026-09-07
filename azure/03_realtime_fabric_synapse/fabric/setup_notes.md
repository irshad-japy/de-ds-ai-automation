# Microsoft Fabric setup — beginner walkthrough

This POC uses Fabric for two separate learning paths:

1. **Real-Time Intelligence:** Event Hubs -> Eventstream -> Eventhouse/KQL.
2. **OneLake/Lakehouse:** make curated lake data available in Fabric without unnecessary copying where a shortcut is practical.

> Fabric screens and licensing can change. Use a Fabric-enabled capacity or Trial workspace if your tenant/account allows it.

## A. Create the workspace

1. Open Microsoft Fabric.
2. Select **Workspaces**.
3. Select **New workspace**.
4. Name it `poc03-realtime-fabric`.
5. Make sure the workspace is assigned to Fabric capacity or a supported Trial.
6. Open the workspace.

**Verify**
- The workspace opens successfully.
- You can select **New item**.

## B. Create an Eventhouse

1. In the workspace select **New item**.
2. Search for **Eventhouse**.
3. Create `poc03-eventhouse`.
4. Fabric creates an Eventhouse and a default KQL database.
5. Open the database.

**Verify**
- `poc03-eventhouse` appears in the workspace.
- Its KQL database opens.
- You can create tables/querysets.

## C. Create the KQL table

Open the KQL database/query window and run the commands from:

`../kql/create_shipment_table.kql`

Create the table before wiring the final destination if you want full control over column types.

## D. Create Eventstream and connect Azure Event Hubs

1. Workspace -> **New item** -> **Eventstream**.
2. Name it `poc03-shipment-eventstream`.
3. Add source -> **Azure Event Hubs**.
4. Create/select a connection.
5. Enter/select:
   - Event Hubs namespace
   - Event Hub `shipment-events`
   - consumer group, if requested
6. Preview data. You should see JSON events from the Python producer.
7. Add destination -> **Eventhouse**.
8. Select:
   - Eventhouse: `poc03-eventhouse`
   - database: its KQL database
   - destination table: `ShipmentEvents`
9. Map source JSON fields to the KQL columns.
10. **Publish** the Eventstream.

Important: current Fabric Eventstream uses an edit/publish flow. Changes are not live until published.

**Verify**
- Eventstream Live view shows data flowing.
- Destination is healthy.
- Run:
  `ShipmentEvents | take 10`
- Then run the provided grouped KQL queries.

## E. Create a Lakehouse

1. Workspace -> **New item** -> **Lakehouse**.
2. Name it `poc03_lakehouse`.
3. Open the Lakehouse.

### Shortcut approach

If your environment exposes the ADLS location to OneLake shortcuts:

1. In the Lakehouse, locate **Files** or **Tables**.
2. Select **New shortcut**.
3. Choose the supported ADLS Gen2 source.
4. Authenticate.
5. Point the shortcut at the curated/gold path.
6. Name it `shipment_gold_shortcut`.

If shortcut creation is not available for your tenant or authentication setup, document that limitation and load only the tiny Gold dataset manually for this POC.

**Verify**
- Browse the shortcut/data.
- Confirm no second large data copy was required.

## F. Minimal Fabric transformation

Use a Fabric Notebook, Dataflow Gen2, or Pipeline.

Beginner option: Fabric Notebook.

1. Create a new Notebook in the workspace.
2. Attach `poc03_lakehouse`.
3. Load the shortcut or copied Gold data.
4. Create a tiny curated table named `shipment_summary_fabric`.
5. Verify row counts and totals against the Databricks Gold output.

## G. Semantic model

Create a semantic model over the curated table/Lakehouse/Warehouse as supported by your Fabric workspace.

Measures to demonstrate:

- Total Orders
- Revenue
- Delayed Shipments
- Average Fulfillment Time

See `semantic_model/measures.dax`.

**Verify**
Create four cards in a small report and compare them with the source aggregate.

## H. Real-Time dashboard

Use the KQL database/queryset to create a simple Real-Time dashboard.

Suggested visuals:
- events by 5-minute bin;
- events by event type;
- delayed shipments by region;
- newest event timestamp.

The goal is not dashboard styling; it is to prove low-latency arrival and queryability.
