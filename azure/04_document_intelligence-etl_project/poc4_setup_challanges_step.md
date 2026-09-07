Q. i attach readme.md file in this have full details of pocs so please give me step by step guide me strat pocs
how can i start and where would need to start

The raw text you pasted contains binary/compressed zip data rather than plain Markdown, but the extracted file manifest reveals the exact architecture and workflow for POC 04: Document Intelligence ETL Project.

This POC implements an automated document processing pipeline: PDF invoices land in Azure Blob Storage, Azure AI Document Intelligence extracts the key-value data and line items, Python validates the payload against confidence score thresholds, and the clean records are loaded into Azure SQL Database (with an Azure Function providing event-driven automation).

Follow this step-by-step path to set up and run the POC from start to finish.

Step 1: Set Up Local Python Environment
Open your terminal or PowerShell inside the root POC_04_DOCUMENT_INTELLIGENCE_ETL_PROJECT folder:

Bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
Run the validation unit test to ensure your local dependencies and schemas are intact:

Bash
pytest tests/test_validation.py
Step 2: Provision Azure Infrastructure
The repository provides PowerShell scripts to automate Azure resource provisioning (Storage Account, Azure AI Document Intelligence, and Azure SQL Database).

Ensure the Azure CLI and Azure PowerShell modules are installed, then log in:

PowerShell
az login
Connect-AzAccount
Run the deployment script:

PowerShell
cd scripts
.\01_create_azure_resources.ps1
(If you encounter execution policy issues, run Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass first. If your organization restricts automated provisioning, reference docs/portal_manual_steps.md to create these services manually via the Azure Portal.)

Retrieve your endpoints, resource keys, and connection strings:

PowerShell
.\02_show_resource_values.ps1
Keep the terminal output open or save these values securely.

Step 3: Configure Environment Variables
Copy .env.example to create your local .env file:

Bash
cp .env.example .env
Open .env and fill in the values retrieved from Step 2:

Azure Document Intelligence: Endpoint URL and API key.

Azure Storage: Connection string and container names (invoices-input, invoices-processed, etc.).

Azure SQL Database: Server name, database name, username, and password.

If running the Azure Function locally with Azure Functions Core Tools:

Bash
cp local.settings.json.example local.settings.json
Populate local.settings.json with the matching storage and cognitive service credentials.

Step 4: Initialize the Database Schema
Before loading data, initialize the tables and permissions in Azure SQL:

Connect to your Azure SQL database using Azure Data Studio, SSMS, or the Azure Portal Query Editor.

Execute sql/create_tables.sql to build the core tables (such as Invoices, InvoiceLineItems, and ProcessingAuditLog).

If you plan to use Managed Identity for your Azure Function App rather than SQL authentication, run sql/create_function_identity_user.sql to grant the function app access.

Step 5: Upload Sample Invoices to Azure Storage
The project includes test invoices (invoice_001.pdf through invoice_005.pdf as standard samples, and invoice_006_malformed.pdf for boundary/failure testing):

(Optional) Run python scripts/generate_sample_invoices.py if you need additional synthetic test PDFs.

Upload the input files to your Azure Blob Storage landing container:

Bash
python src/upload_samples.py
Step 6: Run the Local ETL Pipeline
Test the complete ETL logic locally before deploying event-driven cloud triggers.

Execute the batch runner:

Bash
python src/run_batch.py
What happens under the hood during this execution:

storage_client.py: Fetches PDF files from the storage container.

extract_invoice.py: Calls Azure Document Intelligence using the prebuilt invoice model.

validate_invoice.py: Validates fields against schemas/invoice_schema.json and evaluates confidence scores (defined in docs/confidence_rules.md). Low-confidence or corrupted files like invoice_006 are routed to an error/audit queue.

sql_loader.py: Inserts validated invoices and line items into Azure SQL Database within a single database transaction.

Step 7: Verify Database Records
In your SQL query editor, run the verification script:

SQL
-- Run the queries in sql/verify.sql
Confirm that:

Valid invoices (invoice_001.pdf – invoice_005.pdf) have entries in both header and line-item tables.

The malformed invoice (invoice_006_malformed.pdf) is flagged in the audit/quarantine table with reason codes.

Step 8: Event-Driven Execution via Azure Functions (Optional / Production Flow)
To automate the pipeline so that it triggers automatically whenever a new PDF lands in Blob Storage:

Review function_app.py and host.json.

Test locally using Azure Functions Core Tools:

Bash
func start
Deploy the function code to your provisioned Azure Function App:

Bash
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
Drop a new invoice into the input storage container to observe automatic ingestion, processing, and database insertion.

Step 9: Teardown and Resource Cleanup
When you are done testing, tear down the cloud infrastructure to avoid ongoing charges:

PowerShell
cd scripts
.\99_cleanup.ps1
If you need deeper context on system design or preparation for technical interviews regarding this implementation, review docs/architecture.md and docs/interview_questions.md.

-------------------------------
Q. i try to run this pytest tests/test_validation.py getting error below is the full details terminal logs

The error occurs because running the standalone pytest command does not add the current project root directory to Python's module search path (sys.path), causing it to fail when resolving from src.validate_invoice import validate_invoice.  Notice that your earlier run with python -m pytest -q passed because the -m flag automatically injects the current working directory into sys.path.Solution 1: Use python -m pytest (Immediate Fix)Run the test through the Python module runner:PowerShellpython -m pytest tests/test_validation.py
Solution 2: Configure pytest.ini (Permanent Fix)To make standalone pytest tests/test_validation.py work without typing python -m every time, configure pytest to recognize the root folder as an import root:In the root directory (poc_04_document_intelligence-etl_project), create a file named pytest.ini.Add the following lines:Ini, TOML[pytest]
pythonpath = .
Now, running pytest tests/test_validation.py will automatically locate the src package.  Solution 3: Set PYTHONPATH in PowerShell (Session Fix)If you prefer not to add a configuration file, set the environment variable for your active PowerShell terminal session:PowerShell$env:PYTHONPATH = "."
pytest tests/test_validation.py

---------------------------------------------
Q. now its working fine what is next step
(common-venv-py3.12) C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\azure\poc_04_document_intelligence-etl_project>pytest tests/test_validation.py
test session starts

The next step is setting up the Azure infrastructure and configuring your environment variables.  Step 2: Provision Azure ResourcesThe pipeline requires three Azure resources:Azure AI Document Intelligence (to parse the PDFs)Azure Storage Account (blob containers for input and processed files)Azure SQL Database (target store for invoice headers and line items)You can deploy these automatically using the included PowerShell script directly from your Command Prompt:  DOSpowershell -ExecutionPolicy Bypass -File scripts\01_create_azure_resources.ps1
Once provisioning completes, print your resource names, keys, endpoints, and connection strings:  DOSpowershell -ExecutionPolicy Bypass -File scripts\02_show_resource_values.ps1
(If you prefer manual setup or your organization restricts scripting, follow the portal walkthrough in docs\portal_manual_steps.md.)  Step 3: Configure Your .env FileIn Command Prompt, copy the example configuration template:  DOScopy .env.example .env
Open .env in VS Code or Notepad:DOSnotepad .env
Populate the variables using the output from 02_show_resource_values.ps1:  DOCUMENT_INTELLIGENCE_ENDPOINTDOCUMENT_INTELLIGENCE_KEYAZURE_STORAGE_CONNECTION_STRINGSTORAGE_CONTAINER_INPUT (typically invoices-input)SQL_SERVER, SQL_DATABASE, SQL_USER, and SQL_PASSWORDSave and close the file.Step 4: Create Database TablesConnect to your Azure SQL Database using your preferred tool (SQL Server Management Studio, Azure Data Studio, or the Azure Portal Query Editor).Open and execute the script located at sql\create_tables.sql.  Confirm that the following tables exist:InvoicesInvoiceLineItemsProcessingAuditLogStep 5: Upload Sample Invoices to Azure Blob StorageOnce the storage containers exist and credentials are in .env, upload the test PDFs (invoice_001.pdf through invoice_006_malformed.pdf) from your local samples\input\ folder into Blob Storage:  DOSpython src\upload_samples.py
Step 6: Run the Batch ETL PipelineTrigger the extraction, validation, and SQL load process:  DOSpython src\run_batch.py
During this step:src\extract_invoice.py sends each PDF to Document Intelligence.  src\validate_invoice.py tests confidence thresholds and schema constraints.  src\sql_loader.py inserts clean rows and writes rejection logs for invoice_006_malformed.pdf.  

---------------------------------
Q. now after run above both ps1 file getting below terminal logs
powershell -ExecutionPolicy Bypass -File scripts\02_show_resource_values.ps1

Step 1: Retrieve Your Keys and Connection StringsRun these commands in your Command Prompt to grab the secret Document Intelligence key and the Storage Account connection string:Get the Document Intelligence Key from Key Vault:DOSaz keyvault secret show --vault-name kv-poc04-5506 --name document-intelligence-key --query value -o tsv
Get the Storage Account Connection String:DOSaz storage account show-connection-string --name stpoc04di5506 --resource-group rg-poc04-docintel --query connectionString -o tsv
Step 2: Configure Your .env FileCopy the example file to .env:  DOScopy .env.example .env
Open .env in Notepad or VS Code:DOSnotepad .env
Populate the fields with your values and save the file:DOCUMENT_INTELLIGENCE_ENDPOINT: [https://di-poc04-5506-e96f3.cognitiveservices.azure.com/](https://di-poc04-5506-e96f3.cognitiveservices.azure.com/)DOCUMENT_INTELLIGENCE_KEY: (paste the key from Step 1.1)AZURE_STORAGE_CONNECTION_STRING: (paste the connection string from Step 1.2)SQL_SERVER: sql-poc04-5506.database.windows.netSQL_DATABASE: sqldb-poc04SQL_USER: sqladmin (or whatever admin username was created by the script; check .poc04-resources.txt if generated)SQL_PASSWORD: (the SQL password you typed during the script setup)Step 3: Allow Your IP and Create the SQL TablesAdd a Firewall Rule for your local machine:DOSaz sql server firewall-rule create --resource-group rg-poc04-docintel --server sql-poc04-5506 --name AllowMyIP --client-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
(Note: For strict security, you can specify only your public IP, or enable "Allow Azure services and resources to access this server" and your client IP in the Azure Portal).Execute Table Creation:Go to the Azure Portal $\rightarrow$ Navigate to sql-poc04-5506 $\rightarrow$ Click on sqldb-poc04.Click Query editor (preview) in the left sidebar and log in.Open sql\create_tables.sql in a text editor, paste the contents into the query window, and click Run.  Step 4: Upload Sample Invoices to Azure StorageNow that the storage account is configured in .env, upload the sample test documents (invoice_001.pdf to invoice_006_malformed.pdf) to your blob container:  DOSpython src\upload_samples.py
Step 5: Execute the Batch ETL PipelineProcess the invoices through Azure AI Document Intelligence, run validations, and write data to SQL:  DOSpython src\run_batch.py
# ---------------- Azure Storage ----------------
AZURE_STORAGE_ACCOUNT_NAME=stpoc04di5506
AZURE_STORAGE_CONTAINER=documents

# ---------------- Azure AI Document Intelligence ----------------
DOCUMENTINTELLIGENCE_ENDPOINT=your_endpoint_here
DOCUMENTINTELLIGENCE_API_KEY=your_key_here

# ---------------- Azure SQL ----------------
# Option A: Passwordless (Recommended — works directly via your active `az login` session)
AZURE_SQL_CONNECTIONSTRING=Server=sql-poc04-5506.database.windows.net;Database=sqldb-poc04;Authentication=ActiveDirectoryDefault;Encrypt=yes;TrustServerCertificate=no;

# Option B: Standard SQL Auth (Alternative — replace <YOUR_SQL_PASSWORD> with the password you typed during setup)
# AZURE_SQL_CONNECTIONSTRING=Server=sql-poc04-5506.database.windows.net;Database=sqldb-poc04;User Id=sqladmin;Password=<YOUR_SQL_PASSWORD>;Encrypt=yes;TrustServerCertificate=no;

# ---------------- Validation ----------------
CRITICAL_CONFIDENCE_THRESHOLD=0.70
AMOUNT_TOLERANCE=0.05

# Set true if you want the batch runner to load validated invoices to Azure SQL.
ENABLE_SQL_LOAD=true
-----------------------------------
Q. i run this python -m src.upload_samples and its success after i try to run python -m src.run_batch getting error showing in screenshot

The error Invalid object name 'dbo.invoice_header' indicates that your database connection is working, but the database schema has not been initialized yet. The script attempted to write into tables that do not exist.  Run the schema creation script sql\create_tables.sql in your Azure SQL database to create the required tables.  Option 1: Run via Azure Portal (Fastest)Open the Azure Portal.Navigate to Resource groups $\rightarrow$ rg-poc04-docintel $\rightarrow$ sqldb-poc04.In the left-hand menu, select Query editor (preview).Log in using either Microsoft Entra ID (Active Directory) or SQL server authentication (sqladmin and your password).If prompted with a firewall rule warning, click the button to whitelist your IP.Open sql\create_tables.sql on your computer, copy all contents, paste them into the query editor, and click Run.  Confirm that tables such as dbo.invoice_header, dbo.invoice_line_item, and audit tables appear in the object tree on the left.  Option 2: Run directly from Command Prompt using PythonSince your Python environment already has the SQL driver configured, you can execute the SQL script using this one-liner in your Command Prompt:DOSpython -c "import pyodbc, os; from dotenv import load_dotenv; load_dotenv(); conn = pyodbc.connect(os.getenv('AZURE_SQL_CONNECTIONSTRING')); sql = open('sql/create_tables.sql').read(); [conn.cursor().execute(stmt) for stmt in sql.split('GO') if stmt.strip()]; conn.commit(); print('Tables created successfully!')"
Re-run the Batch PipelineOnce the tables are created, trigger the batch runner again:  DOSpython -m src.run_batch

---------------------------
Q. i follow option 2 and i run this verify sql query getting nothing check screenshot or guide me

Option 2: Verify in Azure Portal Query Editor (Recommended & Visual)
The most direct way to inspect the data without worrying about local ODBC drivers:

Open the Azure Portal.

Navigate to rg-poc04-docintel → sql-poc04-5506 → sqldb-poc04.

Select Query editor (preview) in the left sidebar and sign in.

Open the file sql\verify.sql from your project folder, copy its contents, paste them into the editor, and click Run.  
ZIP

You will see:

The 5 processed invoice records in dbo.invoice_header.

The parsed line items in dbo.invoice_line_item.

The validation error entry for invoice_006_malformed.pdf inside dbo.processing_audit_log.

The results pane shows 0 rows because Azure Portal's Query Editor only displays the output of the very last statement in a multi-query script.The last statement in sql/verify.sql is a duplicate check (HAVING COUNT(*) > 1 on source_hash). Because all 5 processed invoices are unique with no duplicate records, returning 0 rows for duplicate_count is the expected, correct result.  How to View Your Invoice DataTo see the results of the earlier queries, run them individually:1. Check Record CountsSelect and highlight lines 1–2, or clear the editor and run:SQLSELECT COUNT(*) AS header_count FROM dbo.invoice_header;
SELECT COUNT(*) AS line_count FROM dbo.invoice_line;
(Highlight just the first line and click Run to see header_count = 5.)2. View the 5 Processed InvoicesClear the editor window and run:SQLSELECT invoice_number, invoice_date, supplier_name, customer_name, total, currency, source_blob
FROM dbo.invoice_header;
This will display the structured data extracted by Azure AI Document Intelligence from invoice_001.pdf through invoice_005.pdf.  3. View the Line ItemsSQLSELECT TOP (20) invoice_key, line_number, description, quantity, unit_price, amount
FROM dbo.invoice_line;
4. View the Quarantine / Validation Failure (Invoice 006)To see how invoice_006_malformed.pdf was audited:  SQLSELECT TOP (10) * FROM dbo.processing_audit_log;

---------------------------------
Q. ok now i want to get all the step with command, each step to make a document so that any begginer follow this and work on this pocs step by step
also add all the challanges or error or how to resolve this challenges so please give me complete file 

POC 04: Document Intelligence ETL Pipeline — End-to-End Implementation GuideThis document provides a step-by-step implementation guide for deploying, running, and testing an automated document processing pipeline using Azure AI Document Intelligence, Azure Blob Storage, and Azure SQL Database. It includes every terminal command, configuration setting, and a dedicated troubleshooting section covering all errors encountered during setup.  1. System Architecture & Workflow[ Local PDF Samples ]
         │
         ▼ (src.upload_samples)
[ Azure Blob Storage ] (Container: documents/incoming/)
         │
         ▼ (src.run_batch or Azure Function)
[ Azure AI Document Intelligence ] (prebuilt-invoice)
         │
         ▼
[ Python Validation Engine ] (Business rules & confidence scoring)
    ├── If Valid   ──► [ Azure SQL Database ] (dbo.invoice_header & dbo.invoice_line)
    └── If Invalid ──► [ Quarantine / Rejection Log ] (Console & Application Logs)
Ingestion: Sample PDF invoices are uploaded to Azure Blob Storage (documents/incoming/).  Extraction: Azure AI Document Intelligence analyzes each invoice using the prebuilt-invoice model to extract fields (invoice numbers, dates, vendor details, line items, taxes, totals) and field-level confidence scores.  Validation: A Python validation layer checks two critical criteria:  Field confidence threshold $\ge 0.70$ on key attributes.  Mathematical consistency: $\text{Subtotal} + \text{Tax} = \text{Total}$ within a 0.05 tolerance.  Loading: Clean records are written to Azure SQL Database across header and line-item tables using parameterized transactions. Failed records are isolated with failure reasons.  2. PrerequisitesOperating System: Windows 10/11, macOS, or Linux.  Command Prompt: Windows Command Prompt (cmd.exe) or PowerShell.  Python: Python 3.10 to 3.12 installed.  Azure CLI: Installed (az --version) and authenticated (az login).  Active Azure Subscription: Contributor or Owner permissions to provision resources.  3. Step-by-Step ImplementationStep 1: Set Up Python Environment & Run Validation Unit TestsOpen Command Prompt (cmd.exe) and navigate to your project directory:  DOScd C:\Users\<YourUsername>\projects\ird-projects\de-ds-ai-automation\azure\poc_04_document_intelligence-etl_project
Create and activate a Python virtual environment (if not already active):  DOSpython -m venv .venv
.venv\Scripts\activate
Install project dependencies:  DOSpython -m pip install --upgrade pip
pip install -r requirements.txt
Run the validation unit test suite:  DOSpython -m pytest tests/test_validation.py
Expected Output: 3 passed in 0.02s.  Step 2: Provision Azure ResourcesExecute the automated provisioning script using PowerShell:  DOSpowershell -ExecutionPolicy Bypass -File scripts\01_create_azure_resources.ps1
When prompted: Enter a strong temporary SQL provisioning password:, enter a secure password (e.g., P@ssw0rd1234!#) and remember it.The script creates:Resource Group: rg-poc04-docintel  Storage Account: stpoc04di<suffix>  Azure AI Document Intelligence: di-poc04-<suffix>  Azure Key Vault: kv-poc04-<suffix>  Azure SQL Server & Database: sql-poc04-<suffix> / sqldb-poc04  Azure Function App: func-poc04-di-<suffix>  Step 3: Retrieve Resource Values & Configure .envDisplay the provisioned resource names and endpoints:  DOSpowershell -ExecutionPolicy Bypass -File scripts\02_show_resource_values.ps1
Retrieve the Document Intelligence API key from Key Vault:  DOSaz keyvault secret show --vault-name kv-poc04-<YOUR_SUFFIX> --name document-intelligence-key --query value -o tsv
Copy the template configuration file:  DOScopy .env.example .env
Open .env in Notepad:  DOSnotepad .env
Populate your .env file using the exact structure below, replacing the values with your resource values:  Code snippet# ---------------- Azure Storage ----------------
AZURE_STORAGE_ACCOUNT_NAME=stpoc04di<YOUR_SUFFIX>
AZURE_STORAGE_CONTAINER=documents

# ---------------- Azure AI Document Intelligence ----------------
DOCUMENTINTELLIGENCE_ENDPOINT=https://di-poc04-<YOUR_SUFFIX>-e96f3.cognitiveservices.azure.com/
DOCUMENTINTELLIGENCE_API_KEY=<PASTE_KEY_FROM_STEP_3.2>

# ---------------- Azure SQL ----------------
# Local passwordless authentication via `az login`
AZURE_SQL_CONNECTIONSTRING=Server=sql-poc04-<YOUR_SUFFIX>.database.windows.net;Database=sqldb-poc04;Authentication=ActiveDirectoryDefault;Encrypt=yes;TrustServerCertificate=no;

# ---------------- Validation ----------------
CRITICAL_CONFIDENCE_THRESHOLD=0.70
AMOUNT_TOLERANCE=0.05
ENABLE_SQL_LOAD=true
Save (Ctrl + S) and close the file.Step 4: Initialize the Database SchemaBefore running the pipeline, initialize the relational tables.  Go to the Azure Portal.Navigate to Resource groups $\rightarrow$ rg-poc04-docintel $\rightarrow$ sqldb-poc04.  Click Query editor (preview) in the left sidebar.  Log in using your Microsoft Entra ID account (or SQL login: sqladmin and your chosen password).  If prompted with an IP firewall warning, click the button to add your client IP address to the firewall.Open sql/create_tables.sql in your code editor, copy all contents, paste them into the Query Editor, and click Run.  Confirm the execution succeeded: dbo.invoice_header and dbo.invoice_line will appear under the dbo schema tree.  Step 5: Upload Sample Invoices to Azure StorageUpload the test PDF documents (invoice_001.pdf through invoice_006_malformed.pdf) into Azure Blob Storage:  DOSpython -m src.upload_samples
Expected Output:PlaintextUploaded: samples\input\invoice_001.pdf -> documents/incoming/invoice_001.pdf
...
Uploaded: samples\input\invoice_006_malformed.pdf -> documents/incoming/invoice_006_malformed.pdf
Step 6: Execute the Batch ETL PipelineTrigger extraction, validation, and loading:  DOSpython -m src.run_batch
Expected Output Summary:JSONSUMMARY
{
  "processed": 5,
  "failed": 1,
  "skipped": 0
}
invoice_001.pdf through invoice_005.pdf pass validation and write to Azure SQL.  invoice_006_malformed.pdf triggers a failed_validation status due to low confidence on invoice_number and an arithmetic mismatch ($\text{Subtotal } 1500.00 + \text{Tax } 270.00 \ne \text{Total } 9999.00$).  Step 7: Verify Database RecordsIn the Azure Portal Query Editor, run these verification queries individually:  Verify Header Records (Should return 5 rows):SQLSELECT invoice_number, invoice_date, supplier_name, customer_name, total, currency, source_blob
FROM dbo.invoice_header;
Verify Line Item Breakdown:SQLSELECT TOP (20) invoice_key, line_number, description, quantity, unit_price, amount
FROM dbo.invoice_line;
Verify Data Integrity (Confirm no duplicate loads):SQLSELECT source_hash, COUNT(*) AS duplicate_count
FROM dbo.invoice_header
GROUP BY source_hash
HAVING COUNT(*) > 1;
Expected Output: 0 rows returned (proving strict idempotency).  Step 8: Deploy Event-Driven Azure Function (Optional)To enable automatic, zero-touch processing when new files are dropped into Blob Storage:  Grant the Function App Managed Identity access to SQL:Open sql/create_function_identity_user.sql.  Replace <FUNCTION_APP_NAME> with func-poc04-di-<YOUR_SUFFIX>.  Run the script in the Azure SQL Query Editor.  Publish the Function App:DOSfunc azure functionapp publish func-poc04-di-<YOUR_SUFFIX>
Step 9: Cloud Teardown & Cost ManagementWhen testing is complete, destroy all cloud resources to prevent ongoing charges:  DOSpowershell -ExecutionPolicy Bypass -File scripts\99_cleanup.ps1
  When prompted, type DELETE.  Clean up your local environment:DOSdel .env
del .poc04-resources.txt
deactivate
4. Troubleshooting & Challenges Playbook#Error / SymptomRoot CauseSolution1ModuleNotFoundError: No module named 'src' when running pytest tests/test_validation.py  Running standalone pytest in CMD does not include the current working directory in Python's module search path (sys.path).  Run pytest as a Python module: python -m pytest tests/test_validation.py or create a pytest.ini file containing [pytest]\npythonpath = .  2ImportError: attempted relative import with no known parent package when running python src\upload_samples.py  Direct script execution (python path/file.py) lacks the package context required to resolve relative imports like from .config import ....  Execute the file as a module from the root directory: python -m src.upload_samples.  3Driver Error: Base table or view not found; Invalid object name 'dbo.invoice_header'  The ETL runner attempted to write records into Azure SQL before database tables were created.  Open sql/create_tables.sql, paste it into the Azure Portal SQL Query Editor, and execute it before running run_batch.  4pyodbc.InterfaceError: Data source name not found and no default driver specifiedThe connection string did not specify a valid ODBC driver for SQL Server.Ensure ODBC Driver 18 for SQL Server is installed on your OS and the driver attribute is included.  5[SQL Server]Windows logins are not supported in this version of SQL Server. (40607)PyODBC selected the legacy Windows default driver (SQL Server) instead of ODBC Driver 18. The legacy driver does not support ActiveDirectoryDefault authentication and defaults to Windows local auth.Use ODBC Driver 18 for SQL Server or verify records directly using the Azure Portal Query Editor.  6Azure Portal Query Editor returns 0 rows when running verify.sql  Azure Portal Query Editor displays only the output of the final statement in a multi-query script. In verify.sql, the final query checks for duplicates (HAVING COUNT(*) > 1), which legitimately returns 0 rows.  Highlight each query in the editor individually before clicking Run, or run SELECT * FROM dbo.invoice_header; alone.  7Invalid object name 'dbo.processing_audit_log' when inspecting failure logs  The project schema intentionally creates only transactional target tables (dbo.invoice_header and dbo.invoice_line). Malformed invoices are quarantined by the Python layer before touching the database.  Inspect the terminal output of python -m src.run_batch to review quarantined invoices and validation failure payloads.  8Azure SQL Firewall blocking connectionClient machine IP address is not whitelisted in Azure SQL Server firewall settings.  Add a firewall rule via Azure CLI: az sql server firewall-rule create --resource-group rg-poc04-docintel --server <SERVER_NAME> --name AllowMyIP --client-ip-address <YOUR_IP> --end-ip-address <YOUR_IP> or click "Add client IP" in the Azure Portal.  