# Original manual setup notes supplied for the Terraform update

To start this POC, begin in the Azure Portal to set up the infrastructure and storage before configuring Unity Catalog and running notebooks in Azure Databricks.  
MD

Step 1: Provision Azure Infrastructure & Storage
Create the Resource Group:  
MD

Go to portal.azure.com > Resource groups > Create.  
MD

Name: rg-azde-poc02.  
MD

Choose your preferred region (use this same region for all components).  
MD

Create the ADLS Gen2 Storage Account:  
MD

Search Storage accounts > Create.  
MD

Resource Group: rg-azde-poc02.  
MD

Storage account name: unique alphanumeric name, e.g., stazdepoc02<unique_id>.  
MD

Redundancy: LRS.  
MD

Crucial Step: Under the Advanced tab, check Enable hierarchical namespace to make it an ADLS Gen2 account.  
MD

Click Review + Create > Create.  
MD

Create the Storage Container and Directories:  
MD

Inside your storage account, navigate to Data storage > Containers > + Container.  
MD

Name: poc02 (Private access).  
MD

Inside poc02, create the following folder paths:  
MD

raw/orders/

  
MD

raw/customers/

  
MD

checkpoints/

  
MD

schema/

  
MD

quarantine/

  
MD

Step 2: Configure Azure Managed Identity & IAM Permissions
Create Databricks Access Connector:  
MD

Search Access Connector for Azure Databricks > Create.  
MD

Name: ac-azde-poc02 in rg-azde-poc02.  
MD

Identity type: System-assigned managed identity.  
MD

After deployment, open ac-azde-poc02 and copy the Resource ID:  
MD

Plaintext
/subscriptions/<subscription-id>/resourceGroups/rg-azde-poc02/providers/Microsoft.Databricks/accessConnectors/ac-azde-poc02
Grant RBAC Role to the Access Connector:  
MD

Open your Storage Account > Access Control (IAM) > Add role assignment.  
MD

Role: Storage Blob Data Contributor.  
MD

Assign access to: Managed identity > Access Connector for Azure Databricks > Select ac-azde-poc02.  
MD

Click Review + assign.  
MD

Step 3: Set Up Databricks Workspace & Unity Catalog
Create Azure Databricks Workspace:  
MD

Search Azure Databricks > Create.  
MD

Name: dbw-azde-poc02 in rg-azde-poc02.  
MD

Choose Serverless or Standard/Premium workspace tier.  
MD

Deploy and click Launch Workspace.  
MD

Configure Storage Credential in Unity Catalog:  
MD

In Databricks, go to Catalog > + Add > Create a credential / Storage credential.  
MD

Name: poc02_storage_cred.  
MD

Credential type: Azure Managed Identity.  
MD

Paste the copied Access Connector Resource ID and save.  
MD

Create the External Location:  
MD

Go to Catalog > + Add > Create an external location.  
MD

Name: poc02_ext.  
MD

Storage URL: abfss://poc02@<YOUR_STORAGE_ACCOUNT>.dfs.core.windows.net/

  
MD

Storage Credential: poc02_storage_cred.  
MD

Grant your Databricks user permissions: READ FILES, WRITE FILES, CREATE EXTERNAL TABLE, CREATE MANAGED STORAGE.  
MD

Spin Up Compute:  
MD

Use Serverless compute, or create a single-node development cluster under Compute with Auto-termination set to 15 minutes to prevent unnecessary costs.  
MD

Step 4: Import Code & Upload Phase-1 Data
Import Notebooks:  
MD

In Databricks Workspace, create a folder POC_02_DATABRICKS_MEDALLION_CDC and import the Python files from notebooks/ (or clone the repository via Git Folders).  
MD
+ 1

Upload Phase-1 Files via Azure Storage Explorer/Portal:  
MD

Upload sample_data/phase1/raw/orders/orders_batch_001.csv to poc02/raw/orders/.  
MD

Upload sample_data/phase1/raw/customers/customers_batch_001.csv to poc02/raw/customers/.  
MD

Do not upload Phase-2 files yet.

  
MD

Step 5: Execute Initial Pipeline (Phase 1)
Set the widget parameters at the top of each notebook:

storage_account: <YOUR_STORAGE_ACCOUNT>

  
MD

container: poc02

  
MD

catalog: azde_poc

  
MD

Execute the notebooks in sequence:

Run notebooks/00_setup.py:  
MD

Creates the azde_poc catalog and schemas: bronze, silver, gold, quarantine.  
MD

Run notebooks/01_bronze_ingest.py:  
MD

Set batch_id = phase1.  
MD

Ingests CSVs using Auto Loader (cloudFiles) into azde_poc.bronze.orders and azde_poc.bronze.customers.  
MD

Test: Rerun the notebook immediately without new files to verify the streaming checkpoint prevents duplicate ingestion.  
MD

Run notebooks/02_silver_quality.py:  
MD

Applies schema enforcement, business typing, quarantine routing for invalid records, and deduplication.  
MD

Run notebooks/03_gold_dimensions.py:  
MD

Generates gold.fact_orders (with Delta Change Data Feed enabled), gold.dim_product (SCD Type 1), and gold.dim_customer (SCD Type 2).  
MD
+ 2

Step 6: Test Incremental Loads, Schema Evolution & CDF (Phase 2)
Upload Phase-2 Data:  
MD

Upload orders_batch_002_schema_evolution.csv to poc02/raw/orders/.  
MD

Upload customers_batch_002_customer_change.csv to poc02/raw/customers/.  
MD

Run 01_bronze_ingest.py (with batch_id = phase2):  
MD

The newly discovered column sales_channel triggers Auto Loader schema evolution. If it stops on the first execution to update schema metadata, run it once more to ingest the batch.  
MD
+ 1

Rerun 02_silver_quality.py and 03_gold_dimensions.py:  
MD

Verifies Delta MERGE upserts, SCD Type 2 history creation for modified customer records, and fact table updates.  
MD

Run notebooks/04_cdf_consumer.py:  
MD

Consumes incremental changes from fact_orders and writes the change feed to azde_poc.gold.fact_orders_changes_audit.  
MD

Step 7: Automation & Validation
Run Validation Queries:  
MD

Execute queries in sql/validation_queries.sql to check data consistency across Bronze, Silver, Gold, and Quarantine.  
MD

Automate via Workflows:  
MD

Create a Databricks Job chaining the notebooks in order: 00_setup → 01_bronze_ingest → 02_silver_quality → 03_gold_dimensions → 04_cdf_consumer.  
MD

Terminate Compute:  
MD

Shut down your classic cluster immediately after running tests to avoid idle costs.  
MD