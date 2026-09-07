/*
POC-01: business validation + idempotent MERGE + file log + watermark.

Important behavior:
- ADF Copy Activity handles type-incompatible rows before this procedure.
- This procedure handles semantic/business-rule invalid rows.
- Watermark and SUCCEEDED file log are updated only inside the successful transaction.
*/

CREATE OR ALTER PROCEDURE dbo.usp_merge_orders
    @pipeline_name VARCHAR(100),
    @source_file   VARCHAR(500),
    @run_id        VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @staging_rows INT = 0;
    DECLARE @reject_rows INT = 0;
    DECLARE @valid_rows INT = 0;

    IF EXISTS (
        SELECT 1
        FROM dbo.etl_file_log
        WHERE source_file = @source_file
          AND status = 'SUCCEEDED'
    )
    BEGIN
        -- File-level idempotency safeguard. Pipeline Lookup should normally skip before this point.
        RETURN;
    END;

    BEGIN TRY
        BEGIN TRANSACTION;

        SELECT @staging_rows = COUNT(*)
        FROM dbo.orders_stg
        WHERE source_file = @source_file
          AND pipeline_run_id = @run_id;

        -- Record type-compatible rows that violate business rules.
        INSERT INTO dbo.orders_rejects (
            order_id,
            customer_id,
            order_ts,
            product_id,
            quantity,
            unit_price,
            status,
            source_file,
            pipeline_run_id,
            reject_reason
        )
        SELECT
            s.order_id,
            s.customer_id,
            s.order_ts,
            s.product_id,
            s.quantity,
            s.unit_price,
            s.status,
            s.source_file,
            s.pipeline_run_id,
            CONCAT(
                CASE WHEN s.order_id IS NULL OR s.order_id <= 0 THEN 'order_id must be greater than 0; ' ELSE '' END,
                CASE WHEN s.customer_id IS NULL OR s.customer_id <= 0 THEN 'customer_id must be greater than 0; ' ELSE '' END,
                CASE WHEN s.order_ts IS NULL THEN 'order_ts is required; ' ELSE '' END,
                CASE WHEN s.product_id IS NULL OR s.product_id <= 0 THEN 'product_id must be greater than 0; ' ELSE '' END,
                CASE WHEN s.quantity IS NULL OR s.quantity <= 0 THEN 'quantity must be greater than 0; ' ELSE '' END,
                CASE WHEN s.unit_price IS NULL OR s.unit_price < 0 THEN 'unit_price must be zero or greater; ' ELSE '' END,
                CASE WHEN s.status IS NULL OR s.status NOT IN ('NEW','PAID','SHIPPED','CANCELLED') THEN 'status is invalid; ' ELSE '' END
            )
        FROM dbo.orders_stg AS s
        WHERE s.source_file = @source_file
          AND s.pipeline_run_id = @run_id
          AND (
                s.order_id IS NULL OR s.order_id <= 0
             OR s.customer_id IS NULL OR s.customer_id <= 0
             OR s.order_ts IS NULL
             OR s.product_id IS NULL OR s.product_id <= 0
             OR s.quantity IS NULL OR s.quantity <= 0
             OR s.unit_price IS NULL OR s.unit_price < 0
             OR s.status IS NULL OR s.status NOT IN ('NEW','PAID','SHIPPED','CANCELLED')
          );

        SET @reject_rows = @@ROWCOUNT;

        SELECT @valid_rows = COUNT(*)
        FROM dbo.orders_stg AS s
        WHERE s.source_file = @source_file
          AND s.pipeline_run_id = @run_id
          AND s.order_id > 0
          AND s.customer_id > 0
          AND s.order_ts IS NOT NULL
          AND s.product_id > 0
          AND s.quantity > 0
          AND s.unit_price >= 0
          AND s.status IN ('NEW','PAID','SHIPPED','CANCELLED');

        MERGE dbo.orders AS tgt
        USING (
            SELECT
                order_id,
                customer_id,
                order_ts,
                product_id,
                quantity,
                unit_price,
                status,
                source_file
            FROM dbo.orders_stg
            WHERE source_file = @source_file
              AND pipeline_run_id = @run_id
              AND order_id > 0
              AND customer_id > 0
              AND order_ts IS NOT NULL
              AND product_id > 0
              AND quantity > 0
              AND unit_price >= 0
              AND status IN ('NEW','PAID','SHIPPED','CANCELLED')
        ) AS src
        ON tgt.order_id = src.order_id
        WHEN MATCHED THEN
            UPDATE SET
                tgt.customer_id = src.customer_id,
                tgt.order_ts = src.order_ts,
                tgt.product_id = src.product_id,
                tgt.quantity = src.quantity,
                tgt.unit_price = src.unit_price,
                tgt.status = src.status,
                tgt.source_file = src.source_file,
                tgt.updated_ts = SYSUTCDATETIME()
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (
                order_id,
                customer_id,
                order_ts,
                product_id,
                quantity,
                unit_price,
                status,
                source_file,
                created_ts,
                updated_ts
            )
            VALUES (
                src.order_id,
                src.customer_id,
                src.order_ts,
                src.product_id,
                src.quantity,
                src.unit_price,
                src.status,
                src.source_file,
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            );

        -- Staging is transient. Only clear rows for this file/run so parallel files do not interfere.
        DELETE FROM dbo.orders_stg
        WHERE source_file = @source_file
          AND pipeline_run_id = @run_id;

        MERGE dbo.etl_file_log AS tgt
        USING (
            SELECT
                @source_file AS source_file,
                @pipeline_name AS pipeline_name,
                @run_id AS pipeline_run_id,
                CAST('SUCCEEDED' AS VARCHAR(30)) AS status,
                @staging_rows AS staging_rows,
                @reject_rows AS sql_reject_rows,
                @valid_rows AS curated_rows
        ) AS src
        ON tgt.source_file = src.source_file
        WHEN MATCHED THEN
            UPDATE SET
                pipeline_name = src.pipeline_name,
                pipeline_run_id = src.pipeline_run_id,
                status = src.status,
                staging_rows = src.staging_rows,
                sql_reject_rows = src.sql_reject_rows,
                curated_rows = src.curated_rows,
                processed_ts = SYSUTCDATETIME(),
                error_message = NULL
        WHEN NOT MATCHED THEN
            INSERT (
                source_file, pipeline_name, pipeline_run_id, status,
                staging_rows, sql_reject_rows, curated_rows, processed_ts, error_message
            )
            VALUES (
                src.source_file, src.pipeline_name, src.pipeline_run_id, src.status,
                src.staging_rows, src.sql_reject_rows, src.curated_rows, SYSUTCDATETIME(), NULL
            );

        MERGE dbo.etl_watermark AS tgt
        USING (
            SELECT
                @pipeline_name AS pipeline_name,
                SYSUTCDATETIME() AS last_success_ts,
                @run_id AS last_run_id,
                @source_file AS last_source_file
        ) AS src
        ON tgt.pipeline_name = src.pipeline_name
        WHEN MATCHED THEN
            UPDATE SET
                last_success_ts = src.last_success_ts,
                last_run_id = src.last_run_id,
                last_source_file = src.last_source_file
        WHEN NOT MATCHED THEN
            INSERT (pipeline_name, last_success_ts, last_run_id, last_source_file)
            VALUES (src.pipeline_name, src.last_success_ts, src.last_run_id, src.last_source_file);

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;

        THROW;
    END CATCH;
END;
GO

PRINT 'dbo.usp_merge_orders is ready.';
GO
