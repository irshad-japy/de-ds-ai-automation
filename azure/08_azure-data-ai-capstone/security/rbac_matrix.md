# RBAC matrix

| Persona / workload | Scope | Minimum demo role | Purpose |
|---|---|---|---|
| Developer | ADLS account/container | Storage Blob Data Contributor | Upload/read POC files |
| Event sender | Event Hubs namespace/hub | Azure Event Hubs Data Sender | Send shipment events |
| Event receiver | Event Hubs namespace/hub | Azure Event Hubs Data Receiver | Consume shipment events |
| Search index builder | Search service | Search Service Contributor + Search Index Data Contributor | Create index and load documents |
| Search runtime | Search service | Search Index Data Reader | Query only |
| Foundry app/user | Foundry project | Azure AI User (or org-approved equivalent) | Call project/model/agent |
| Document extractor | Document Intelligence | Cognitive Services User, or key stored in Key Vault | Analyze invoices |
| SQL reader | Azure SQL DB | contained Entra user with SELECT only | Agent analytical tool |

For the first beginner run, keys/connection strings can be used where explicitly supported in `.env.example`; migrate to Entra/RBAC once the flow works.
