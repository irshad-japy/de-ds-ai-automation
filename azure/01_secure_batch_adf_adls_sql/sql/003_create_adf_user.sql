/*
POC-01: create Azure SQL contained database user for ADF system-assigned Managed Identity.

Run as the configured Microsoft Entra administrator while connected to the TARGET database.
Replace <ADF_NAME> before execution.
*/

SET NOCOUNT ON;
GO

DECLARE @adf_name SYSNAME = N'<ADF_NAME>';

IF @adf_name = N'<ADF_NAME>' OR @adf_name = N''
BEGIN
    THROW 50001, 'Replace <ADF_NAME> with the exact Azure Data Factory resource name before running this script.', 1;
END;

DECLARE @sql NVARCHAR(MAX);

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = @adf_name)
BEGIN
    SET @sql = N'CREATE USER ' + QUOTENAME(@adf_name) + N' FROM EXTERNAL PROVIDER;';
    EXEC sys.sp_executesql @sql;
END;

-- Least-privilege permissions required by this POC.
SET @sql = N'GRANT SELECT, INSERT ON dbo.orders_stg TO ' + QUOTENAME(@adf_name) + N';';
EXEC sys.sp_executesql @sql;

SET @sql = N'GRANT SELECT ON dbo.etl_file_log TO ' + QUOTENAME(@adf_name) + N';';
EXEC sys.sp_executesql @sql;

SET @sql = N'GRANT EXECUTE ON dbo.usp_merge_orders TO ' + QUOTENAME(@adf_name) + N';';
EXEC sys.sp_executesql @sql;

PRINT 'ADF contained database user and POC permissions are ready.';
GO
