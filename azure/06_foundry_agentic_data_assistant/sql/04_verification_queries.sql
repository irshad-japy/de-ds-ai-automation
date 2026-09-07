EXEC dbo.usp_GetRevenueByRegion @StartDate='2026-09-01', @EndDate='2026-09-02';
EXEC dbo.usp_GetDelayedShipments @ReportDate='2026-09-02';
EXEC dbo.usp_GetOrderSummary @OrderId=1001;
EXEC dbo.usp_GetMetricSource @MetricName='revenue';
