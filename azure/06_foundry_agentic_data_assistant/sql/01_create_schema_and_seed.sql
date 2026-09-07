-- POC-06 sample schema. Run in your Azure SQL database as an administrator.
-- This script creates a small deterministic dataset for the POC.

IF OBJECT_ID('dbo.Orders', 'U') IS NOT NULL DROP TABLE dbo.Orders;
GO

CREATE TABLE dbo.Orders (
    order_id INT NOT NULL PRIMARY KEY,
    order_date DATE NOT NULL,
    region NVARCHAR(50) NOT NULL,
    revenue DECIMAL(18,2) NOT NULL,
    shipment_status NVARCHAR(30) NOT NULL,
    delay_reason NVARCHAR(250) NULL
);
GO

INSERT INTO dbo.Orders(order_id, order_date, region, revenue, shipment_status, delay_reason) VALUES
(1001, '2026-09-01', 'South', 1250.50, 'Delayed', 'Carrier capacity constraint'),
(1002, '2026-09-01', 'West',   980.00,  'Delivered', NULL),
(1003, '2026-09-02', 'North',  2210.25, 'Delayed', 'Weather disruption'),
(1004, '2026-09-02', 'South',  600.00,  'Delivered', NULL),
(1005, '2026-09-02', 'West',   1750.75, 'Delayed', 'Address verification hold'),
(1006, '2026-09-03', 'North',  400.00,  'Processing', NULL);
GO
