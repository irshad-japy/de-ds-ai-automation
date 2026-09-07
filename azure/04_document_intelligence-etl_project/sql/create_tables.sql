IF OBJECT_ID('dbo.invoice_line', 'U') IS NOT NULL DROP TABLE dbo.invoice_line;
IF OBJECT_ID('dbo.invoice_header', 'U') IS NOT NULL DROP TABLE dbo.invoice_header;
GO

CREATE TABLE dbo.invoice_header (
    invoice_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    source_hash CHAR(64) NOT NULL UNIQUE,
    invoice_number NVARCHAR(100) NULL,
    invoice_date DATE NULL,
    supplier_name NVARCHAR(250) NULL,
    customer_name NVARCHAR(250) NULL,
    currency NVARCHAR(10) NULL,
    subtotal DECIMAL(18,2) NULL,
    tax DECIMAL(18,2) NULL,
    total DECIMAL(18,2) NULL,
    source_blob NVARCHAR(500) NOT NULL,
    document_confidence FLOAT NULL,
    processed_at DATETIME2 NOT NULL CONSTRAINT DF_invoice_header_processed_at DEFAULT SYSUTCDATETIME()
);
GO

CREATE TABLE dbo.invoice_line (
    invoice_line_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    invoice_key BIGINT NOT NULL,
    line_number INT NOT NULL,
    description NVARCHAR(500) NULL,
    quantity DECIMAL(18,4) NULL,
    unit_price DECIMAL(18,2) NULL,
    amount DECIMAL(18,2) NULL,
    CONSTRAINT FK_invoice_line_header FOREIGN KEY (invoice_key)
        REFERENCES dbo.invoice_header(invoice_key)
);
GO

CREATE INDEX IX_invoice_line_invoice_key ON dbo.invoice_line(invoice_key);
GO
