# Cleanup

Do this after screenshots/evidence are saved.

## Fastest Azure cleanup

If ALL resources for this POC were created only inside:

`rg-poc03-realtime-dev`

then delete the resource group:

1. Azure portal -> Resource groups.
2. Open `rg-poc03-realtime-dev`.
3. Select **Delete resource group**.
4. Type the resource group name.
5. Confirm deletion.

This removes the Azure resources inside it.

## Before deleting

- Export screenshots.
- Save KQL/SQL results.
- Record Event Hubs metrics.
- Record Databricks validation results.
- Verify Gold output.
- Save Fabric screenshots/report.

## Databricks

Even before deleting the resource group:
- terminate compute;
- verify no cluster/SQL warehouse is still running.

## Fabric

Fabric resources are not necessarily deleted with the Azure resource group.

Delete POC-only:
- Eventstream;
- Eventhouse/KQL DB;
- Lakehouse/Warehouse;
- Notebook/Pipeline/Dataflow;
- Semantic model/report;
- workspace, if it exists only for this POC.

If using a Trial/capacity, review it separately.

## Purview / Log Analytics

Delete only if they were created solely for this POC and you are sure they are not shared.
