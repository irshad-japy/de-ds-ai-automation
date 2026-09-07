# Azure portal setup — beginner path

Use this only for resources you are not reusing from POC-01 through POC-07.

## 1. Resource group
1. Azure portal -> **Resource groups** -> **Create**.
2. Subscription: your lab subscription.
3. Name: `rg-poc08-capstone`.
4. Region: choose one region supported by your services.
5. Review + create.

## 2. ADLS Gen2
1. **Storage accounts** -> Create.
2. Put it in `rg-poc08-capstone`.
3. Standard / LRS is enough for the lab.
4. On Advanced, enable **Hierarchical namespace**.
5. After deployment, Data storage -> Containers -> create `datalake`.
6. For passwordless access, IAM -> Add role assignment -> **Storage Blob Data Contributor** to your user.
7. Put `https://<account>.dfs.core.windows.net` in `ADLS_ACCOUNT_URL`.

## 3. Event Hubs
1. **Event Hubs** -> Create namespace.
2. Use Standard for a straightforward POC.
3. Create event hub `shipment-events` with 2 partitions.
4. IAM -> assign **Azure Event Hubs Data Sender** and **Azure Event Hubs Data Receiver** to your user for passwordless local testing.
5. Put `<namespace>.servicebus.windows.net` in `.env`.

## 4. Databricks
Reuse the POC-02 workspace if possible. Upload the three files from `lakehouse/bronze`, `lakehouse/silver`, and `lakehouse/gold` as notebooks. Create only temporary job/interactive compute, run the notebooks, then terminate it.

For ADLS access, reuse your POC-02 Unity Catalog / service principal / managed identity approach. Replace the `<storage>` placeholder in notebook widget defaults or pass real ABFSS paths at run time.

## 5. Serving layer
Choose **one** for the minimal capstone: existing Azure SQL, Synapse serverless, or Fabric. Do not provision all three unless you specifically need to demonstrate them.

For Azure SQL, run `serving/sql/schema.sql`, then use `serving.sql.load_gold`.

## 6. Document Intelligence
1. Create/reuse a **Document Intelligence** resource.
2. Copy its endpoint and key into `.env` for the first run.
3. Run the prebuilt invoice test on `data/synthetic/invoice_001.pdf`.
4. Later, store the key in Key Vault or move to Entra-based authentication according to your organization standards.

## 7. Azure AI Search
1. Create/reuse an **Azure AI Search** service.
2. Free can be sufficient for a lab if your subscription/region permits it; otherwise use the smallest acceptable paid tier temporarily.
3. Put endpoint in `AZURE_SEARCH_ENDPOINT`.
4. Beginner path: copy an admin key to `AZURE_SEARCH_ADMIN_KEY` for index creation and a query key to `AZURE_SEARCH_QUERY_KEY` for querying.
5. Better path: use Search RBAC roles and leave keys blank.

## 8. Microsoft Foundry
1. Open Microsoft Foundry and create/reuse a project.
2. Deploy a chat model; put its deployment name in `FOUNDRY_MODEL_DEPLOYMENT`.
3. Copy the **project endpoint** in the form `https://<resource>.services.ai.azure.com/api/projects/<project>` to `.env`.
4. Deploy an embeddings model such as `text-embedding-3-small` on an Azure OpenAI-compatible endpoint and configure `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`.
5. The Foundry project endpoint is used for Responses/agent calls; embeddings use the Azure OpenAI `/openai/v1` endpoint.

## 9. Local authentication choices

### Choice A — easiest when Azure CLI is not installed
Set:

```env
AZURE_AUTH_MODE=browser
```

The Python scripts use `InteractiveBrowserCredential` and open a browser login when Entra authentication is needed.

### Choice B — Azure CLI
Install Azure CLI, close/reopen terminal, then:

```powershell
az --version
az login
az account show
```

Set `AZURE_AUTH_MODE=default`. `DefaultAzureCredential` can then use the Azure CLI sign-in.

### Choice C — keys / connection strings for first POC run
Fill the explicit connection-string/key values in `.env.example`. This is easier but less production-like. Never commit `.env`.
