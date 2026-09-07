# Architecture — POC-01 Secure Batch Landing Zone

## Goal

Build a small but production-shaped Azure batch ingestion flow using identity-based authentication and GitHub-safe configuration.

```text
Local Python generator
        |
        | az login + DefaultAzureCredential (developer identity)
        v
ADLS Gen2
landing/orders/YYYY/MM/DD/orders_001.csv
        |
        | ADF system-assigned Managed Identity
        v
Azure Data Factory
  1. Get Metadata (file exists?)
  2. Lookup (already processed?)
  3. Copy CSV -> Azure SQL orders_stg
     - incompatible rows redirected to ADLS quarantine
     - source file path + ADF RunId added as audit columns
  4. Stored Procedure validates business rules + MERGE
  5. Copy raw file landing -> archive
  6. Delete landing copy
  7. On processing failure, copy original file to quarantine
        |
        v
Azure SQL Database
  dbo.orders_stg       transient typed staging
  dbo.orders           curated idempotent target
  dbo.orders_rejects   business-rule rejects
  dbo.etl_file_log     new-file/idempotency control
  dbo.etl_watermark    latest successful pipeline timestamp
        |
        +--> ADF Monitor
        +--> Optional Log Analytics
```

## Security model

- **Developer -> ADLS:** Microsoft Entra identity via `az login`; no storage key in source code.
- **ADF -> ADLS:** ADF system-assigned managed identity with `Storage Blob Data Contributor` at the storage account or narrower container scope.
- **ADF -> Azure SQL:** ADF system-assigned managed identity is created as a contained database user and receives only the permissions needed for staging, lookup, and stored procedure execution.
- **Key Vault:** included to practice secret-management patterns. The main data path deliberately does not require a secret because Managed Identity is preferred.
- **GitHub:** no passwords, access keys, SAS tokens, tenant secrets, `.tfvars`, state files, or generated credentials are committed.

## Networking model for the beginner lab

The base lab uses public service endpoints plus strong identity authentication. Azure SQL may need the "Allow Azure services and resources to access this server" firewall setting when ADF uses Azure Integration Runtime. This is a deliberate learning simplification.

For a hardened enterprise version, use ADF Managed Virtual Network plus managed private endpoints / Private Link for ADLS, Azure SQL, and Key Vault.

## Data quality model

The sample generator deliberately creates two bad rows:

1. `quantity = -2` — type is valid but violates the business rule. It reaches staging and is recorded in `dbo.orders_rejects`.
2. `unit_price = NOT_A_PRICE` — incompatible with `DECIMAL(12,2)`. ADF Copy Activity skips it and redirects the incompatible row log to the quarantine path.

With 30 generated rows, the expected curated result is **28 valid business rows**.
