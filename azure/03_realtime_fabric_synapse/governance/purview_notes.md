# Purview / governance notes

Purview is intentionally optional in this learning POC because account availability,
permissions, and cost can vary.

## If Purview is available

Keep the scope tiny.

1. Open your Microsoft Purview account/portal.
2. Register only the relevant source(s), for example:
   - the POC ADLS Gen2 account;
   - the Synapse workspace, if supported in your environment.
3. Create credentials/managed identity access as required.
4. Scan only the `realtime` container or smallest practical scope.
5. Review:
   - discovered assets;
   - schema;
   - classifications;
   - lineage where available.
6. Capture screenshots/notes for your project evidence.
7. Stop/delete scan schedules you do not need.

## If Purview is NOT available

Do not claim it was deployed.

Document the intended enterprise design:

- Purview Data Map catalogs Event Hubs downstream data stores, ADLS, Synapse, and Fabric-supported assets.
- Scan rules classify technical metadata and sensitive fields.
- Lineage helps trace source -> processing -> curated/serving layers where connectors expose it.
- Access governance remains separate from cataloging: Azure RBAC/ACLs, Fabric permissions,
  Databricks/Unity Catalog controls, and SQL permissions still matter.
- In production, scans should be scheduled and scoped rather than scanning everything indiscriminately.

## Evidence checklist

- [ ] Purview actually deployed, OR clearly marked "design only"
- [ ] Tiny scan scope documented
- [ ] Classification screenshot/notes
- [ ] Lineage screenshot/notes if supported
- [ ] No credentials committed to Git
