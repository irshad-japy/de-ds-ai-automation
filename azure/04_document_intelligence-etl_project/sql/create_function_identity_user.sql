-- Run this while connected as the Microsoft Entra administrator of the Azure SQL logical server.
-- Replace <FUNCTION_APP_NAME> with the Azure Function App's exact system-assigned managed identity name.
CREATE USER [<FUNCTION_APP_NAME>] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [<FUNCTION_APP_NAME>];
ALTER ROLE db_datawriter ADD MEMBER [<FUNCTION_APP_NAME>];
GO
