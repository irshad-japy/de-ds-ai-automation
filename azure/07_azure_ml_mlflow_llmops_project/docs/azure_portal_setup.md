# Azure Portal setup — beginner path

## 1. Create a resource group
1. Open **portal.azure.com**.
2. Search **Resource groups** -> **Create**.
3. Subscription: choose your learning subscription.
4. Resource group: `rg-poc07-mlops`.
5. Region: choose a region available to your subscription and near your data.
6. **Review + create** -> **Create**.

## 2. Create Azure Machine Learning workspace
1. Azure Portal -> **Create a resource**.
2. Search **Machine Learning** -> select **Azure Machine Learning** -> **Create**.
3. Subscription: same as above.
4. Resource group: `rg-poc07-mlops`.
5. Workspace name: for example `mlw-poc07-mlops-<initials>`.
6. Region: same region if practical.
7. For a first POC, accept the default dependent resources (storage, Key Vault, Application Insights; container registry is created when needed by deployment).
8. **Review + create** -> **Create**.

## 3. Understand storage
The Azure ML workspace has a default Azure Storage account and default datastores such as `workspaceblobstore`. This POC registers the local CSV as a data asset, which uploads it to workspace-managed storage.

Important: the workspace **default** storage account is not an ADLS Gen2 hierarchical-namespace account. If you specifically want ADLS Gen2 practice, create a separate ADLS Gen2 storage account and attach it as an additional datastore later. It is not required for this POC.

## 4. Open Azure Machine Learning studio
From the workspace, select **Launch studio** (or open `ml.azure.com`) and select the workspace.

You will later verify:
- **Data** -> the registered training data asset;
- **Jobs/Experiments** -> the two MLflow runs;
- **Models** -> the selected registered model version;
- **Endpoints** -> the temporary batch endpoint during validation.

## 5. Fill local `.env`
In the project folder:
```bat
copy .env.example .env
```
Edit `.env` and fill:
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZUREML_WORKSPACE_NAME`

You can copy the subscription ID from Azure Portal -> **Subscriptions**. The resource group/workspace names are the names you just created. No client secret is required for the interactive beginner flow.
