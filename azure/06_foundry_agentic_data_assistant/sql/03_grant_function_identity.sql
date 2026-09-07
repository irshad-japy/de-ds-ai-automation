-- IMPORTANT: Replace <FUNCTION_APP_IDENTITY_NAME> before running.
-- Run while connected as the Microsoft Entra administrator of the Azure SQL server.
-- Least privilege: grant EXECUTE only on the four approved stored procedures.

CREATE USER [<FUNCTION_APP_IDENTITY_NAME>] FROM EXTERNAL PROVIDER;
GO

GRANT EXECUTE ON OBJECT::dbo.usp_GetRevenueByRegion TO [<FUNCTION_APP_IDENTITY_NAME>];
GRANT EXECUTE ON OBJECT::dbo.usp_GetDelayedShipments TO [<FUNCTION_APP_IDENTITY_NAME>];
GRANT EXECUTE ON OBJECT::dbo.usp_GetOrderSummary TO [<FUNCTION_APP_IDENTITY_NAME>];
GRANT EXECUTE ON OBJECT::dbo.usp_GetMetricSource TO [<FUNCTION_APP_IDENTITY_NAME>];
GO

-- Intentionally DO NOT add db_datawriter, db_owner, or ALTER permissions.
