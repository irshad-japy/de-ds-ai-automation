-- The application calls ONLY these approved stored procedures.
-- No model-generated SQL is ever accepted.

CREATE OR ALTER PROCEDURE dbo.usp_GetRevenueByRegion
    @StartDate DATE,
    @EndDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT region, CAST(SUM(revenue) AS DECIMAL(18,2)) AS revenue
    FROM dbo.Orders
    WHERE order_date >= @StartDate AND order_date <= @EndDate
    GROUP BY region
    ORDER BY region;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetDelayedShipments
    @ReportDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT order_id, order_date, region, shipment_status, delay_reason
    FROM dbo.Orders
    WHERE order_date = @ReportDate AND shipment_status = 'Delayed'
    ORDER BY order_id;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetOrderSummary
    @OrderId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT order_id, order_date, region, revenue, shipment_status, delay_reason
    FROM dbo.Orders
    WHERE order_id = @OrderId;
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetMetricSource
    @MetricName NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        @MetricName AS metric_name,
        CASE LOWER(@MetricName)
            WHEN 'revenue' THEN 'dbo.Orders.revenue; sum by order_date range and region.'
            WHEN 'delayed_shipments' THEN 'dbo.Orders where shipment_status = Delayed; filtered by order_date.'
            ELSE 'Unknown metric. No governed source definition is available.'
        END AS source_description;
END;
GO
