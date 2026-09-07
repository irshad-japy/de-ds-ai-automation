/*
POC-01: core Azure SQL objects
Run in the target Azure SQL Database (for example sqldb-azde-poc01-dev).
Safe to rerun: objects are created only when absent.
*/

SET NOCOUNT ON;
GO

IF OBJECT_ID('dbo.orders_stg', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.orders_stg (
        order_id          BIGINT          NULL,
        customer_id       BIGINT          NULL,
        order_ts          DATETIME2(0)    NULL,
        product_id        BIGINT          NULL,
        quantity          INT             NULL,
        unit_price        DECIMAL(12,2)   NULL,
        status            VARCHAR(30)     NULL,
        source_file       VARCHAR(500)    NOT NULL,
        pipeline_run_id   VARCHAR(100)    NOT NULL,
        load_ts           DATETIME2(0)    NOT NULL CONSTRAINT DF_orders_stg_load_ts DEFAULT SYSUTCDATETIME()
    );

    CREATE INDEX IX_orders_stg_file_run
        ON dbo.orders_stg (source_file, pipeline_run_id);
END;
GO

IF OBJECT_ID('dbo.orders', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.orders (
        order_id          BIGINT          NOT NULL CONSTRAINT PK_orders PRIMARY KEY,
        customer_id       BIGINT          NOT NULL,
        order_ts          DATETIME2(0)    NOT NULL,
        product_id        BIGINT          NOT NULL,
        quantity          INT             NOT NULL,
        unit_price        DECIMAL(12,2)   NOT NULL,
        status            VARCHAR(30)     NOT NULL,
        source_file       VARCHAR(500)    NOT NULL,
        created_ts        DATETIME2(0)    NOT NULL CONSTRAINT DF_orders_created_ts DEFAULT SYSUTCDATETIME(),
        updated_ts        DATETIME2(0)    NOT NULL CONSTRAINT DF_orders_updated_ts DEFAULT SYSUTCDATETIME()
    );
END;
GO

IF OBJECT_ID('dbo.orders_rejects', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.orders_rejects (
        reject_id         BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_orders_rejects PRIMARY KEY,
        order_id          BIGINT          NULL,
        customer_id       BIGINT          NULL,
        order_ts          DATETIME2(0)    NULL,
        product_id        BIGINT          NULL,
        quantity          INT             NULL,
        unit_price        DECIMAL(12,2)   NULL,
        status            VARCHAR(30)     NULL,
        source_file       VARCHAR(500)    NOT NULL,
        pipeline_run_id   VARCHAR(100)    NOT NULL,
        reject_reason     VARCHAR(1000)   NOT NULL,
        reject_ts         DATETIME2(0)    NOT NULL CONSTRAINT DF_orders_rejects_reject_ts DEFAULT SYSUTCDATETIME()
    );

    CREATE INDEX IX_orders_rejects_file
        ON dbo.orders_rejects (source_file, reject_ts);
END;
GO

IF OBJECT_ID('dbo.etl_file_log', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.etl_file_log (
        source_file       VARCHAR(500)    NOT NULL CONSTRAINT PK_etl_file_log PRIMARY KEY,
        pipeline_name     VARCHAR(100)    NOT NULL,
        pipeline_run_id   VARCHAR(100)    NOT NULL,
        status            VARCHAR(30)     NOT NULL,
        staging_rows      INT             NULL,
        sql_reject_rows   INT             NULL,
        curated_rows      INT             NULL,
        processed_ts      DATETIME2(0)    NOT NULL CONSTRAINT DF_etl_file_log_processed_ts DEFAULT SYSUTCDATETIME(),
        error_message     VARCHAR(2000)   NULL,
        CONSTRAINT CK_etl_file_log_status CHECK (status IN ('SUCCEEDED', 'FAILED'))
    );
END;
GO

IF OBJECT_ID('dbo.etl_watermark', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.etl_watermark (
        pipeline_name     VARCHAR(100)  NOT NULL CONSTRAINT PK_etl_watermark PRIMARY KEY,
        last_success_ts   DATETIME2(0)  NULL,
        last_run_id       VARCHAR(100)  NULL,
        last_source_file  VARCHAR(500)  NULL
    );
END;
GO

PRINT 'POC-01 tables are ready.';
GO
