# Optional Self-hosted Integration Runtime (SHIR) lab

Do this only after the main Azure-native POC works.

## When SHIR is needed

Use Self-hosted Integration Runtime when ADF must reach a data store that is not directly reachable by Azure Integration Runtime, such as:

- local/on-premises file system,
- on-premises SQL Server,
- private network resources without an Azure-native managed private connectivity path,
- specific network-isolated systems.

## Safe beginner lab

1. In ADF Studio → Manage → Integration runtimes.
2. Create a Self-hosted IR.
3. Install it on your own Windows laptop.
4. Register it using the ADF-provided setup flow.
5. Use a tiny local CSV folder as source.
6. Copy the CSV to ADLS landing or Azure SQL.
7. Do not open inbound public ports on your laptop/router.
8. Stop/uninstall the lab component when finished if you no longer need it.

## What you should learn

- SHIR initiates outbound connectivity to Azure; you generally do not expose a new inbound public endpoint just for this lab.
- It is a runtime/connectivity component, not a data store.
- For cloud-to-cloud public endpoints, Azure Integration Runtime is normally simpler.
