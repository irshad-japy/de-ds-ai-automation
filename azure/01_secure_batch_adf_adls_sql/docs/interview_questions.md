# Interview questions and short answers

## 1. Why land files in ADLS before Azure SQL?

It decouples ingestion from relational processing, preserves raw source evidence for audit/replay, supports scalable file storage, and lets downstream processing retry without asking the source system to resend data.

## 2. How did you make the ADF pipeline idempotent?

I used two layers. `dbo.etl_file_log` prevents a successfully processed source path from being reprocessed, and the curated SQL table uses `order_id` as a primary/business key with `MERGE` update/insert logic.

## 3. What is a watermark?

A watermark is a persisted marker of successful progress, usually a timestamp or source key. In this POC `dbo.etl_watermark` stores the last successful pipeline time/run/file and is updated only inside the successful SQL transaction.

## 4. Managed Identity vs Key Vault secret?

Managed Identity is preferable when the target supports Microsoft Entra authentication because there is no application secret to store or rotate. Key Vault is used when a real secret/key/certificate is still required.

## 5. Why use a staging table?

Staging isolates ingestion from curated logic. It allows type loading, validation, quality checks, transaction-controlled merge, troubleshooting, and easier replay without writing raw incoming rows directly into the business table.

## 6. How are bad rows handled?

Type-incompatible rows can be skipped/logged by ADF Copy Activity fault tolerance to the quarantine area. Type-compatible rows that violate business rules are inserted into `dbo.orders_rejects` by the merge stored procedure.

## 7. When would you need SHIR?

When ADF must reach on-premises/local or network-isolated sources that Azure Integration Runtime cannot reach directly.

## 8. Why is ADF given Storage Blob Data Contributor?

This POC requires read from landing, write to archive/quarantine, and delete after archive. In a stricter design, I would scope permissions to containers/folders and potentially split identities.

## 9. Why not store the SQL admin password in ADF?

ADF can authenticate to Azure SQL with its system-assigned Managed Identity. A contained database user is created for that identity, removing the need for a pipeline password.

## 10. What happens if the same file is re-uploaded?

The Lookup checks `etl_file_log`; if the file path was already successful, the ingestion branch is skipped. The duplicate raw re-upload can be moved to an archive duplicate folder and deleted from landing.

## 11. How would you scale to thousands of files?

Use folder/file enumeration, metadata-driven control tables, ForEach with controlled parallelism, partitioned landing conventions, event/schedule triggers as appropriate, batching, retry policies, and careful monitoring. For very high throughput, evaluate whether ADF Copy, Spark/Fabric/Synapse/Databricks, or another compute pattern is the better transform engine.

## 12. How would Private Endpoints change the design?

I would disable/restrict public service endpoints, put ADF in Managed Virtual Network, create managed private endpoints to ADLS/SQL/Key Vault, approve private endpoint connections, and account for private DNS/connectivity. Identity authorization is still required; Private Link does not replace RBAC/database permissions.

## 13. Why test by removing RBAC?

It proves the pipeline fails predictably when authorization is missing, the failure is observable, no false success/watermark occurs, and restoring the correct permission allows a safe retry.

## 14. What is the difference between Azure RBAC and SQL database permissions here?

Azure RBAC controls Azure resource/data-plane access such as ADLS. Azure SQL also has its own database authorization model; the ADF Managed Identity must be created as a database principal and granted SQL permissions.
