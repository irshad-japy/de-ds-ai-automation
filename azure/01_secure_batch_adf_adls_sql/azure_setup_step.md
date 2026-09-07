Azure Data Factory: End-to-End Batch Ingestion Pipeline GuideThis document provides complete instructions to configure, deploy, execute, troubleshoot, verify, and clean up the automated batch data ingestion pipeline using Azure Data Factory (ADF), Azure Data Lake Storage Gen2 (ADLS Gen2), and Azure SQL Database with Managed Identity Authentication.  1. Architecture OverviewPlaintext[ADLS Gen2: landing/] 
       │
       ▼
[ADF Pipeline: PL_INGEST_ORDERS_BATCH]
  ├── 1. Get_Metadata_File (Check existence, size)
  ├── 2. If_File_Exists (Branching logic)
  │       ├── True  ──► Continue Pipeline
  │       └── False ──► Fail_File_Not_Found
  ├── 3. Script_Log_Start (Log IN_PROGRESS to SQL)
  ├── 4. Copy_Orders_To_Staging (ADLS CSV -> SQL orders_stg)
  ├── 5. SP_Merge_Orders (Execute usp_merge_orders: Stage -> Target)
  ├── 6. Copy_Archive_File (Binary Copy: landing/ -> archive/)
  ├── 7. Delete_Landing_File (Purge processed file from landing/)
  └── 8. Script_Log_Success (Update log status to SUCCESS)
  2. ADLS Gen2 Storage Setup2.1 Container ConfigurationIn the Azure Portal, open the storage account (stazdepocirshad01) and create the following containers:  landing — Ingestion entry point for incoming raw batch files.  archive — Target location for preserving processed files.  quarantine — Target location for invalid or unparseable records.  2.2 Sample Test File UploadUpload a test file named orders_001.csv to landing/orders/2026/08/28/orders_001.csv:  Code snippetorder_id,customer_id,order_date,product_id,quantity,unit_price,status
1001,501,2026-08-28,10,2,25.50,Completed
1002,502,2026-08-28,12,1,100.00,Pending
1003,503,2026-08-28,15,4,15.75,Completed
1004,504,2026-08-28,10,1,25.50,Shipped
1005,505,2026-08-28,20,3,45.00,Completed
  3. Azure SQL Database Setup3.1 Server Firewall ConfigurationTo allow Azure Data Factory integration runtimes to reach the database:  Navigate to SQL Server (sql-azde-poc-irshad-01) > Security > Networking.  Under Exceptions, enable "Allow Azure services and resources to access this server".  Click Save.  3.2 ADF Managed Identity Permission ProvisioningConnect to sqldb-azde-poc01-dev as the Microsoft Entra Admin and execute:  SQL-- 1. Create contained database user for ADF Managed Identity
CREATE USER [adf-azde-poc-irshad-01] FROM EXTERNAL PROVIDER;

-- 2. Grant read, write, and schema execution permissions
ALTER ROLE db_datareader ADD MEMBER [adf-azde-poc-irshad-01];
ALTER ROLE db_datawriter ADD MEMBER [adf-azde-poc-irshad-01];
ALTER ROLE db_ddladmin ADD MEMBER [adf-azde-poc-irshad-01];
  3.3 DDL Script (Tables)Execute the following table definitions in Query Editor:  SQL-- 1. ETL File Log Table
IF OBJECT_ID('dbo.etl_file_log', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.etl_file_log (
        log_id INT IDENTITY(1,1) PRIMARY KEY,
        file_name VARCHAR(255) NOT NULL,
        file_size_bytes BIGINT,
        status VARCHAR(50) NOT NULL,
        rows_inserted INT DEFAULT 0,
        rows_updated INT DEFAULT 0,
        started_at DATETIME2,
        completed_at DATETIME2,
        error_message NVARCHAR(MAX)
    );
END;

-- 2. Staging Table
IF OBJECT_ID('dbo.orders_stg', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.orders_stg (
        order_id INT,
        customer_id INT,
        order_date VARCHAR(50),
        product_id INT,
        quantity INT,
        unit_price DECIMAL(10,2),
        status VARCHAR(50)
    );
END;

-- 3. Target Orders Table
IF OBJECT_ID('dbo.orders', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.orders (
        order_id INT PRIMARY KEY,
        customer_id INT,
        order_date DATE,
        product_id INT,
        quantity INT,
        unit_price DECIMAL(10,2),
        total_amount AS (quantity * unit_price) PERSISTED,
        status VARCHAR(50),
        source_file VARCHAR(255),
        created_at DATETIME2 DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 DEFAULT SYSUTCDATETIME()
    );
END;
  3.4 Stored Procedure (Merge Staging to Target)SQLCREATE OR ALTER PROCEDURE dbo.usp_merge_orders
    @p_file_name VARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;

    MERGE dbo.orders AS tgt
    USING (
        SELECT 
            order_id,
            customer_id,
            TRY_CONVERT(DATE, order_date) AS order_date,
            product_id,
            quantity,
            unit_price,
            status
        FROM dbo.orders_stg
    ) AS src
    ON tgt.order_id = src.order_id
    WHEN MATCHED THEN
        UPDATE SET 
            tgt.customer_id = src.customer_id,
            tgt.order_date = src.order_date,
            tgt.product_id = src.product_id,
            tgt.quantity = src.quantity,
            tgt.unit_price = src.unit_price,
            tgt.status = src.status,
            tgt.source_file = @p_file_name,
            tgt.updated_at = SYSUTCDATETIME()
    WHEN NOT MATCHED THEN
        INSERT (order_id, customer_id, order_date, product_id, quantity, unit_price, status, source_file, created_at, updated_at)
        VALUES (src.order_id, src.customer_id, src.order_date, src.product_id, src.quantity, src.unit_price, src.status, @p_file_name, SYSUTCDATETIME(), SYSUTCDATETIME());
END;
  4. Azure Data Factory Configuration4.1 Linked ServicesCreate two linked services with System-assigned Managed Identity:  LS_ADLS_GEN2_MI: Targets stazdepocirshad01.dfs.core.windows.net (Requires Storage Blob Data Contributor role on ADLS).  LS_AZURE_SQL_MI: Targets sql-azde-poc-irshad-01.database.windows.net, Database: sqldb-azde-poc01-dev.  4.2 Parameterized DatasetsDataset 1: DS_ADLS_OrdersCsv (DelimitedText)  Linked Service: LS_ADLS_GEN2_MI  Parameters: p_container (String), p_folder (String), p_file (String)  File system: @dataset().p_container  Directory: @dataset().p_folder  File: @dataset().p_file  First row as header: Checked (True)  Dataset 2: DS_ADLS_Binary (Binary)  Linked Service: LS_ADLS_GEN2_MI  Parameters: p_container (String), p_folder (String), p_file (String)  File system: @dataset().p_container  Directory: @dataset().p_folder  File: @dataset().p_file  Dataset 3: DS_SQL_Table (Azure SQL Database)  Linked Service: LS_AZURE_SQL_MI  Parameters: p_target_table (String)  Schema: dbo  Table: @dataset().p_target_table  5. Pipeline Implementation: PL_INGEST_ORDERS_BATCH5.1 Pipeline ParametersParameter NameTypeDefault Valuep_containerStringlandingp_folderStringorders/2026/08/28p_fileStringorders_001.csvp_target_tableStringorders_stg  5.2 Activities ConfigurationGet_Metadata_File (Get Metadata)  Dataset: DS_ADLS_OrdersCsv  Dataset Parameters: p_container: @pipeline().parameters.p_container, p_folder: @pipeline().parameters.p_folder, p_file: @pipeline().parameters.p_file  Field List: Exists, Size, Last modified  If_File_Exists (If Condition)  Expression: @activity('Get_Metadata_File').output.exists  False Branch: Add Fail activity named Fail_File_Not_Found.  Fail message: @concat('File does not exist: ', pipeline().parameters.p_container, '/', pipeline().parameters.p_folder, '/', pipeline().parameters.p_file)  Error code: FILE_NOT_FOUND  Script_Log_Start (Script Activity) (Success dependency from If_File_Exists)  Linked Service: LS_AZURE_SQL_MI  Script Type: Query  Script Text:SQLINSERT INTO dbo.etl_file_log (file_name, file_size_bytes, status, started_at)
VALUES ('@{pipeline().parameters.p_file}', @{activity('Get_Metadata_File').output.size}, 'IN_PROGRESS', SYSUTCDATETIME());
  Copy_Orders_To_Staging (Copy Data Activity) (Success dependency from Script_Log_Start)  Source: DS_ADLS_OrdersCsv (Parameters bound to pipeline parameters)  Sink: DS_SQL_Table (p_target_table: orders_stg)  Pre-copy script: TRUNCATE TABLE dbo.orders_stg;  SP_Merge_Orders (Stored Procedure Activity) (Success dependency from Copy_Orders_To_Staging)  Linked Service: LS_AZURE_SQL_MI  Stored Procedure Name: [dbo].[usp_merge_orders]  Parameters: p_file_name | Type: String | Value: @pipeline().parameters.p_file  Copy_Archive_File (Copy Data Activity - Binary) (Success dependency from SP_Merge_Orders)  Source: DS_ADLS_Binary (p_container: @pipeline().parameters.p_container, p_folder: @pipeline().parameters.p_folder, p_file: @pipeline().parameters.p_file)  Sink: DS_ADLS_Binary (p_container: archive, p_folder: @pipeline().parameters.p_folder, p_file: @pipeline().parameters.p_file)  Delete_Landing_File (Delete Activity) (Success dependency from Copy_Archive_File)  Dataset: DS_ADLS_Binary (p_container: @pipeline().parameters.p_container, p_folder: @pipeline().parameters.p_folder, p_file: @pipeline().parameters.p_file)  Script_Log_Success (Script Activity) (Success dependency from Delete_Landing_File)  Linked Service: LS_AZURE_SQL_MI  Script Type: Query  Script Text:SQLUPDATE dbo.etl_file_log
SET status = 'SUCCESS',
    rows_inserted = (SELECT COUNT(1) FROM dbo.orders WHERE source_file = '@{pipeline().parameters.p_file}'),
    rows_updated = 0,
    completed_at = SYSUTCDATETIME()
WHERE file_name = '@{pipeline().parameters.p_file}'
  AND status = 'IN_PROGRESS';
  6. Deployment & ExecutionIn Azure Data Factory Studio, click Validate all to confirm 0 errors.  Click Publish all to persist all changes to the Data Factory service.  Click Debug (or Add trigger > Trigger now) with default parameters.  7. Troubleshooting Common ErrorsError A: Fail_File_Not_Found Triggered / Condition Evaluates to FalseRoot Cause: The file is not at landing/orders/2026/08/28/orders_001.csv (e.g., uploaded directly to container root landing/orders_001.csv).  Fix: Either move the file to the structured directory orders/2026/08/28/ or clear the p_folder parameter value during debug execution.  Error B: Script_Log_Start Times Out (1m 15s Failure)Root Cause 1 (Firewall): Azure SQL Server firewall blocked the ADF runtime.  Fix: Go to Azure SQL Server > Networking > Enable "Allow Azure services and resources to access this server".  Root Cause 2 (Authentication/Permission): Database user missing for ADF Managed Identity.  Fix: In SQL Query Editor, execute CREATE USER [your-adf-name] FROM EXTERNAL PROVIDER; and assign db_datareader, db_datawriter, and db_ddladmin roles.  8. End-to-End Verification & POC Test SuiteTEST 1: Database & Storage Verification (Initial Run)Execute in Azure SQL Database Query Editor:  SQL-- 1. Curated target table must contain 5 rows
SELECT * FROM dbo.orders;

-- 2. Staging table must be truncated (0 rows)
SELECT * FROM dbo.orders_stg;

-- 3. Execution logs must show status 'SUCCESS'
SELECT * FROM dbo.etl_file_log ORDER BY log_id DESC;
  Storage Verification:  landing/orders/2026/08/28/orders_001.csv: Must be deleted.  archive/orders/2026/08/28/orders_001.csv: Must be present.  TEST 2: Idempotency & Re-Run Verification (Duplicate Load Prevention)Re-upload orders_001.csv to landing/orders/2026/08/28/orders_001.csv.  In ADF Studio, click Debug with the same default parameters.  Run verification query:  SQLSELECT COUNT(*) AS total_curated_orders FROM dbo.orders;
  
4. Pass Condition: Count remains exactly 5 (no duplicate records inserted due to SQL MERGE logic).  TEST 3: RBAC Security & Controlled Failure TestGo to Storage Account (stazdepocirshad01) > Access Control (IAM) > Role assignments.  Remove Storage Blob Data Contributor from the ADF Managed Identity.  Re-upload a file and run the pipeline.Expected Result: Pipeline immediately fails at Get_Metadata_File with HTTP 403 Forbidden.  Re-grant Storage Blob Data Contributor to the ADF Managed Identity and re-run.  Pass Condition: Pipeline completes successfully, validating role-based security isolation and self-healing recovery.  TEST 4: ADF Monitoring VerificationOpen ADF Studio > Monitor tab > Pipeline runs.  Select the run and inspect Copy_Orders_To_Staging activity details.  Confirm Rows read = 5 and Rows written = 5.  9. Repository Structure & Artifact MappingThe accompanying project package (POC_01_SECURE_BATCH_ADF_ADLS_SQL_FULL_PROJECT.zip) provides:Plaintextpoc_01_secure_batch_adf_adls_sql/
├── README.md                      # Complete project manual & checklist
├── architecture.md               # End-to-end data flow diagrams
├── python/
│   ├── generate_orders.py        # Generates synthetic data with deliberate errors
│   ├── inspect_orders.py         # Local data quality inspector
│   └── upload_to_adls.py         # DefaultAzureCredential ADLS uploader
├── sql/
│   ├── 001_create_tables.sql     # DDL for staging, orders, log, rejects tables
│   ├── 002_merge_orders.sql      # Idempotent MERGE stored procedure
│   ├── 003_create_adf_user.sql   # Managed Identity user grant script
│   ├── 004_verification_queries.sql # Automated validation queries
│   └── 005_reset_lab.sql         # Test reset script
├── adf/
│   ├── pipeline_sanitized.json   # Git-safe pipeline ARM/JSON definition
│   ├── linkedServices/           # Managed Identity linked services
│   └── datasets/                 # Parameterized dataset definitions
├── infra/
│   ├── terraform/                # Complete Terraform IaC setup
│   └── bicep/                    # Storage Bicep comparison module
└── docs/
    ├── security_and_github.md    # Credential hygiene checklist
    ├── monitoring.md             # ADF Monitor & Log Analytics guidance
    └── interview_questions.md    # Scenario-based technical interview prep
  10. Resource Cleanup (Cost Control)After capturing all test screenshots and query outputs:  Navigate to the Azure Portal > Resource groups.  Open rg-azde-poc01-dev.  Click Delete resource group, enter the name to confirm, and delete to stop all compute and storage charges.  