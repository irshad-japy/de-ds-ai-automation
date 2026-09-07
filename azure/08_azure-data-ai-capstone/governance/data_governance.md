# Data governance record

| Dataset | Owner | Classification | Lineage | Access |
|---|---|---|---|---|
| orders raw | Data Engineering | Internal / synthetic | source -> ADF/Python -> ADLS raw | DE contributors |
| orders silver | Data Engineering | Internal / synthetic | raw -> Databricks Bronze -> Silver | DE contributors/readers |
| customer metrics gold | Analytics | Internal / synthetic | Silver -> Gold -> serving/search | analytics readers |
| shipment events | Data Engineering | Internal / synthetic | Event Hubs -> ADLS Bronze | event sender/receiver roles |
| invoice extraction | AI Engineering | Internal / synthetic | PDF -> Document Intelligence -> JSON/search | AI app identity |
| policy knowledge | Business/Data Owner | Internal / synthetic | JSON -> embeddings -> AI Search -> RAG | search reader + Foundry app |

For a real system, map these records into Purview/Unity Catalog and apply organization-specific classification labels and retention policies.
