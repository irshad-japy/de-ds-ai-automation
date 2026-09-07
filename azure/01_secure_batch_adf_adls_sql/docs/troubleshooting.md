# Troubleshooting — POC-01

## 1. Python uploader gets 403 AuthorizationPermissionMismatch / AuthorizationFailure

Likely cause: your **user** lacks a Storage data-plane role.

Fix:

1. Storage Account → IAM.
2. Assign your user `Storage Blob Data Contributor`.
3. Confirm `az account show` is the intended tenant/subscription.
4. Retry after the role assignment is effective.

Remember: Azure resource `Contributor` does not automatically grant blob data read/write.

## 2. ADLS linked service test fails for ADF

Check:

- ADF system-assigned Managed Identity exists.
- ADF identity has `Storage Blob Data Contributor` (or required ACLs/roles).
- Linked service is ADLS Gen2 and uses system-assigned Managed Identity.
- Storage account URL is correct.

## 3. Azure SQL linked service test fails with login/user error

Check in order:

1. SQL logical server has a Microsoft Entra admin.
2. You connected to the **target database**, not just `master`.
3. `sql/003_create_adf_user.sql` used the exact Data Factory resource name.
4. Query `sys.database_principals` for the ADF name.
5. SQL firewall permits the beginner lab's Azure Integration Runtime access.

## 4. `CREATE USER ... FROM EXTERNAL PROVIDER` fails

Typical issues:

- connected using SQL authentication instead of the configured Entra admin;
- wrong tenant/directory;
- the ADF identity was deleted/recreated and now has a new object ID;
- user already exists but maps to an old identity after recreation.

For a recreated Data Factory, the resource name may be the same while its system-assigned identity object is different. Drop/recreate the contained user only if you understand the impact and you have confirmed the identity mismatch.

## 5. Copy Activity fails on `NOT_A_PRICE` instead of skipping it

Open Copy Activity → Settings/Fault tolerance and confirm:

```text
Skip incompatible rows = enabled
Redirect incompatible rows/log = configured to ADLS
```

Also confirm mapping sends `unit_price` to the DECIMAL SQL column.

## 6. Negative quantity reaches curated table

Check that `SP_Validate_Merge` really calls `dbo.usp_merge_orders` and that the current stored procedure contains the business predicate:

```sql
quantity > 0
```

Run `sql/002_merge_orders.sql` again if you created the table but missed the stored procedure script.

## 7. Duplicate re-upload adds rows

Check:

```sql
SELECT * FROM dbo.etl_file_log ORDER BY processed_ts DESC;
```

Then inspect `Lookup_Already_Processed` output in ADF Monitor.

It should return:

```text
processed_count = 1
```

Also run the duplicate business-key query in `sql/004_verification_queries.sql`.

## 8. ADF says file does not exist

Verify pipeline parameters exactly match ADLS, including case/path:

```text
container = landing
folder    = orders/2026/08/28
file      = orders_001.csv
```

Get Metadata with the `exists` field should return false rather than fail when the file is absent.

## 9. Archive copy succeeded but landing file still exists

Check `Delete_Landing_File`:

- dependency must be **Succeeded** from `Copy_Landing_To_Archive`;
- dataset must point to the original landing container/path;
- ADF identity needs write/delete capability on storage.

## 10. Serverless SQL database was paused and ADF failed

A paused serverless Azure SQL Database can make an activity fail while the database is resuming. For a beginner lab, either retry the activity/run or use a small always-available dev SKU if the cost is acceptable.

## 11. Terraform storage/container error

Run:

```powershell
terraform init -upgrade
terraform fmt -recursive
terraform validate
```

Provider behavior evolves. If an `azurerm` argument has changed in a newer provider, use the provider documentation for the pinned major version and update the sample intentionally rather than copying random snippets.

## 12. SQL firewall issue

For the base public-endpoint lab, ADF Azure Integration Runtime needs a server firewall path to Azure SQL. The current Microsoft connector guidance calls out configuring a server-level firewall rule for Azure IR.

For production hardening, do not use public firewall exceptions as the final design; use managed private endpoints/Private Link.
