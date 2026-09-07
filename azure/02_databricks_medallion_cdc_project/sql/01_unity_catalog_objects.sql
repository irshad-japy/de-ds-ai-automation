-- POC-02 Unity Catalog logical objects
-- Storage credential creation is intentionally done in Catalog Explorer because
-- the Azure managed-identity fields are easier for a beginner to verify there.

CREATE CATALOG IF NOT EXISTS azde_poc;
CREATE SCHEMA IF NOT EXISTS azde_poc.bronze;
CREATE SCHEMA IF NOT EXISTS azde_poc.silver;
CREATE SCHEMA IF NOT EXISTS azde_poc.gold;
CREATE SCHEMA IF NOT EXISTS azde_poc.quarantine;

SHOW SCHEMAS IN azde_poc;
SHOW EXTERNAL LOCATIONS;

-- After you create the storage credential in Catalog Explorer, you can optionally
-- create the external location with SQL. Replace both placeholders before running.
--
-- CREATE EXTERNAL LOCATION IF NOT EXISTS poc02_ext
-- URL 'abfss://poc02@<STORAGE_ACCOUNT>.dfs.core.windows.net/'
-- WITH (STORAGE CREDENTIAL poc02_storage_cred)
-- COMMENT 'POC-02 ADLS Gen2 external location';
--
-- Grant only to your own user/group, not to a public identity:
-- GRANT READ FILES, WRITE FILES, CREATE EXTERNAL TABLE
-- ON EXTERNAL LOCATION poc02_ext TO `<YOUR_DATABRICKS_USER_EMAIL>`;
