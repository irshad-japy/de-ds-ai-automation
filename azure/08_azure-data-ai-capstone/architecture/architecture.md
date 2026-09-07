# POC-08 architecture

```mermaid
flowchart TD
    B[Batch orders CSV] --> I[ADF or Python batch upload]
    E[Shipment events] --> EH[Event Hubs]
    D[Synthetic invoice PDF] --> DI[Document Intelligence]
    I --> ADLS[ADLS Gen2]
    EH --> ADLS
    DI --> ADLS
    ADLS --> BR[Databricks Bronze]
    BR --> SI[Databricks Silver]
    SI --> GO[Databricks Gold]
    GO --> SERVE[Fabric / Synapse / Azure SQL]
    GO --> SEARCH[Azure AI Search]
    DI --> SEARCH
    SEARCH --> F[Microsoft Foundry RAG / Agent]
    SERVE --> F
    ML[Optional POC-07 MLflow score] --> F
    F --> A[Data + AI Assistant]

    SEC[Entra ID / RBAC / Key Vault] -.-> ADLS
    SEC -.-> SEARCH
    OBS[Monitor / Log Analytics / App Insights] -.-> F
    OBS -.-> EH
```

## Minimal demo interpretation

You do **not** need to reprovision every service from POC-01 through POC-07. Reuse existing Databricks, SQL/Fabric/Synapse, Document Intelligence and Foundry resources when possible. The capstone demonstrates that the pieces work together and that you can explain identity, governance, observability, CI/CD and cost cleanup.
