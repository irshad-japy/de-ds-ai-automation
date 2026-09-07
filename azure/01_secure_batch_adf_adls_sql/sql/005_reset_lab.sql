/*
Reset only the POC data while keeping schema/procedure intact.
Use when you want to repeat the lab from a clean SQL state.
This does NOT delete Azure resources or ADLS files.
*/

SET NOCOUNT ON;
BEGIN TRANSACTION;

DELETE FROM dbo.orders_stg;
DELETE FROM dbo.orders_rejects;
DELETE FROM dbo.orders;
DELETE FROM dbo.etl_file_log;
DELETE FROM dbo.etl_watermark;

COMMIT TRANSACTION;

PRINT 'POC-01 SQL data reset complete.';
GO
