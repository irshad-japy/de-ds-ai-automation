IF OBJECT_ID('dbo.customer_metrics', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.customer_metrics (
        customer_id NVARCHAR(50) NOT NULL PRIMARY KEY,
        total_orders INT NOT NULL,
        total_units INT NOT NULL,
        total_revenue DECIMAL(18,2) NOT NULL,
        refreshed_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END;
GO

CREATE OR ALTER VIEW dbo.v_customer_metrics AS
SELECT customer_id, total_orders, total_units, total_revenue, refreshed_at
FROM dbo.customer_metrics;
GO
