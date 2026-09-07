# Beginner manual Azure portal setup

Use this if you prefer the Azure portal instead of `scripts/01_create_azure_resources.ps1`.

> Resource names and portal labels can change slightly. The important settings are described below.

## 1. Create a Resource Group

1. Open Azure portal.
2. Search **Resource groups**.
3. Select **Create**.
4. Name: `rg-poc04-docintel`.
5. Region: choose a nearby region where Document Intelligence is available (for India, Central India is a reasonable first check).
6. Review + create.

**Verify:** Open the resource group and confirm its status is active.

## 2. Create ADLS Gen2 data storage

1. Search **Storage accounts** -> **Create**.
2. Resource group: `rg-poc04-docintel`.
3. Give a globally unique lowercase name, for example `stpoc04di1234`.
4. Performance: Standard.
5. Redundancy: LRS for the POC.
6. In **Advanced**, enable **Hierarchical namespace**. This makes the account ADLS Gen2 capable.
7. Disable public blob access where offered.
8. Create.
9. Open the storage account -> **Containers** -> create container `documents`.
10. Inside `documents`, the project will create/use prefixes `incoming/`, `processed/`, and `failed/` automatically.

**RBAC for your laptop:** Storage account -> Access control (IAM) -> Add role assignment -> `Storage Blob Data Contributor` -> your signed-in user.

**Verify:** Upload one synthetic PDF manually into `documents/incoming/`, then delete it again before starting the scripted run.

## 3. Create Azure AI Document Intelligence

1. Search **Document Intelligence** in the Azure portal.
2. Select **Create**.
3. Resource group: `rg-poc04-docintel`.
4. Choose a unique resource name.
5. Choose the same/nearby supported region.
6. Pricing: use **F0** if available for your subscription/region. Do not switch to a paid tier without checking cost.
7. Create the resource.
8. Open the resource -> **Keys and Endpoint**. Copy the endpoint.

For Entra/Managed Identity usage, assign the `Cognitive Services User` role to your user and later to the Function App managed identity.

### Manual Studio test (important)

1. Open Document Intelligence Studio / the current Analyze experience.
2. Select the **Invoice** prebuilt model.
3. Choose your Document Intelligence resource.
4. Upload `samples/input/invoice_001.pdf`.
5. Run analysis.
6. Record: Invoice ID, Invoice Date, Vendor Name, Customer Name, SubTotal, TotalTax, InvoiceTotal, Items and confidence scores.

**Verify:** You should see structured invoice fields rather than only OCR text.

## 4. Create Key Vault

1. Search **Key vaults** -> Create.
2. Resource group: `rg-poc04-docintel`.
3. Choose a unique name.
4. Prefer Azure RBAC permission model for this POC.
5. Create.
6. Give yourself `Key Vault Secrets Officer` if needed.
7. Create secret `document-intelligence-key` only if you want to demonstrate secure secret storage for local key authentication.

Do not commit the key to GitHub. The provided `.gitignore` excludes `.env`.

## 5. Create Azure SQL Database

1. Search **SQL databases** -> Create.
2. Create/select a logical SQL server.
3. Database name: `sqldb-poc04`.
4. For a POC choose the lowest appropriate paid compute tier available to you and review estimated cost before creating. Azure SQL may not have a perpetual free tier in your subscription.
5. Configure Microsoft Entra administrator on the SQL logical server using your signed-in identity.
6. Networking -> add your client IP for local testing only.
7. Use Query Editor, SSMS, or VS Code MSSQL extension and run `sql/create_tables.sql`.

**Verify:** `dbo.invoice_header` and `dbo.invoice_line` exist.

## 6. Create Azure Function App (after local batch works)

1. Search **Function App** -> Create.
2. Runtime stack: Python.
3. Python version: 3.12 (if supported in your selected Function hosting option; otherwise use a supported 3.x version and match your local environment).
4. Enable Application Insights.
5. After creation: Function App -> Identity -> System assigned -> On -> Save.
6. Assign the Function identity:
   - Data storage: `Storage Blob Data Owner` and `Storage Queue Data Contributor` for the POC trigger connection.
   - Document Intelligence: `Cognitive Services User`.
7. In Azure SQL, run `sql/create_function_identity_user.sql` after replacing `<FUNCTION_APP_NAME>`.
8. Configure Function App environment variables using `.env.example` as the guide. Do not add the Document Intelligence API key when using managed identity.

## 7. Application Insights / Monitor verification

After the Function is deployed and receives an invoice:

1. Function App -> Application Insights / Monitor.
2. Check invocations and logs.
3. Search for log messages containing `Invoice trigger received blob` and `Invoice pipeline result`.
4. Confirm success/failure and approximate processing latency from the normalized JSON telemetry.
