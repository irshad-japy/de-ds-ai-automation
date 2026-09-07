# POC-04 resource creation helper (PowerShell + Azure CLI)
# Run from the project root after: az login
# This creates low-cost POC resources. Review names/region before running.

$ErrorActionPreference = "Stop"

$LOCATION = "centralindia"
$SUFFIX = Get-Random -Minimum 1000 -Maximum 9999

$RG = "rg-poc04-docintel"
$DATA_STORAGE = "stpoc04di$SUFFIX"           # must be globally unique, lowercase, <=24 chars
$FUNCTION_STORAGE = "stpoc04fn$SUFFIX"      # separate runtime storage; HNS disabled
$DOC_INTEL = "di-poc04-$SUFFIX"
$KEYVAULT = "kv-poc04-$SUFFIX"
$SQL_SERVER = "sql-poc04-$SUFFIX"
$SQL_DB = "sqldb-poc04"
$FUNCTION_APP = "func-poc04-di-$SUFFIX"

Write-Host "Using suffix: $SUFFIX" -ForegroundColor Cyan
Write-Host "Resource Group: $RG"
Write-Host "Data Storage:  $DATA_STORAGE"
Write-Host "Doc Intel:     $DOC_INTEL"
Write-Host "Key Vault:     $KEYVAULT"
Write-Host "SQL Server:    $SQL_SERVER"
Write-Host "Function App:  $FUNCTION_APP"

# Current signed-in identity for local RBAC / SQL Entra admin.
$USER_OID = az ad signed-in-user show --query id -o tsv
$USER_UPN = az ad signed-in-user show --query userPrincipalName -o tsv

# 1) Resource group
az group create --name $RG --location $LOCATION | Out-Null

# 2) ADLS Gen2 data storage (hierarchical namespace enabled)
az storage account create `
  --name $DATA_STORAGE `
  --resource-group $RG `
  --location $LOCATION `
  --sku Standard_LRS `
  --kind StorageV2 `
  --hierarchical-namespace true `
  --allow-blob-public-access false | Out-Null

$DATA_SCOPE = az storage account show --name $DATA_STORAGE --resource-group $RG --query id -o tsv
az role assignment create --assignee-object-id $USER_OID --assignee-principal-type User --role "Storage Blob Data Contributor" --scope $DATA_SCOPE | Out-Null

# Container/filesystem. Using account key here only for provisioning convenience.
$DATA_KEY = az storage account keys list --account-name $DATA_STORAGE --resource-group $RG --query "[0].value" -o tsv
az storage container create --name documents --account-name $DATA_STORAGE --account-key $DATA_KEY | Out-Null

# 3) Document Intelligence (single-service FormRecognizer kind)
# F0 may be limited to one resource per subscription/region. If F0 fails, review costs before using S0.
az cognitiveservices account create `
  --name $DOC_INTEL `
  --resource-group $RG `
  --location $LOCATION `
  --kind FormRecognizer `
  --sku F0 `
  --yes | Out-Null

$DI_SCOPE = az cognitiveservices account show --name $DOC_INTEL --resource-group $RG --query id -o tsv
$DI_ENDPOINT = az cognitiveservices account show --name $DOC_INTEL --resource-group $RG --query properties.endpoint -o tsv
az role assignment create --assignee-object-id $USER_OID --assignee-principal-type User --role "Cognitive Services User" --scope $DI_SCOPE | Out-Null

# 4) Key Vault (RBAC mode) and local-only storage of the DI key.
az keyvault create --name $KEYVAULT --resource-group $RG --location $LOCATION --enable-rbac-authorization true | Out-Null
$KV_SCOPE = az keyvault show --name $KEYVAULT --resource-group $RG --query id -o tsv
az role assignment create --assignee-object-id $USER_OID --assignee-principal-type User --role "Key Vault Secrets Officer" --scope $KV_SCOPE | Out-Null
Start-Sleep -Seconds 10
$DI_KEY = az cognitiveservices account keys list --name $DOC_INTEL --resource-group $RG --query key1 -o tsv
az keyvault secret set --vault-name $KEYVAULT --name "document-intelligence-key" --value $DI_KEY | Out-Null

# 5) Azure SQL logical server + DB.
# Azure SQL still needs a provisioning SQL administrator credential. The pipeline itself uses Microsoft Entra ID.
$SQL_ADMIN_USER = "pocsqladmin"
$SQL_SECURE = Read-Host "Enter a strong temporary SQL provisioning password" -AsSecureString
$SQL_PTR = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SQL_SECURE)
try {
    $SQL_ADMIN_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($SQL_PTR)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($SQL_PTR)
}

az sql server create `
  --name $SQL_SERVER `
  --resource-group $RG `
  --location $LOCATION `
  --admin-user $SQL_ADMIN_USER `
  --admin-password $SQL_ADMIN_PASSWORD | Out-Null

az sql db create `
  --resource-group $RG `
  --server $SQL_SERVER `
  --name $SQL_DB `
  --service-objective Basic | Out-Null

# Add your current public IP for local development.
$MY_IP = (Invoke-RestMethod -Uri "https://api.ipify.org")
az sql server firewall-rule create --resource-group $RG --server $SQL_SERVER --name AllowMyCurrentIP --start-ip-address $MY_IP --end-ip-address $MY_IP | Out-Null

# Set signed-in user as Microsoft Entra admin.
az sql server ad-admin create --resource-group $RG --server $SQL_SERVER --display-name $USER_UPN --object-id $USER_OID | Out-Null

# 6) Azure Function runtime storage (separate non-HNS storage account)
az storage account create `
  --name $FUNCTION_STORAGE `
  --resource-group $RG `
  --location $LOCATION `
  --sku Standard_LRS `
  --kind StorageV2 `
  --allow-blob-public-access false | Out-Null

# 7) Function App (Linux Consumption)
az functionapp create `
  --resource-group $RG `
  --consumption-plan-location $LOCATION `
  --runtime python `
  --runtime-version 3.12 `
  --functions-version 4 `
  --name $FUNCTION_APP `
  --storage-account $FUNCTION_STORAGE `
  --os-type Linux | Out-Null

$FUNC_ID = az functionapp identity assign --name $FUNCTION_APP --resource-group $RG --query principalId -o tsv

# Function accesses invoice storage through identity-based Blob trigger connection.
az role assignment create --assignee-object-id $FUNC_ID --assignee-principal-type ServicePrincipal --role "Storage Blob Data Owner" --scope $DATA_SCOPE | Out-Null
az role assignment create --assignee-object-id $FUNC_ID --assignee-principal-type ServicePrincipal --role "Storage Queue Data Contributor" --scope $DATA_SCOPE | Out-Null

# Function calls Document Intelligence using Managed Identity.
az role assignment create --assignee-object-id $FUNC_ID --assignee-principal-type ServicePrincipal --role "Cognitive Services User" --scope $DI_SCOPE | Out-Null

# App settings. No Document Intelligence key is stored in Function settings.
$SQL_MI_CONN = "Server=$SQL_SERVER.database.windows.net;Database=$SQL_DB;Authentication=ActiveDirectoryMSI;Encrypt=yes;TrustServerCertificate=no;"
az functionapp config appsettings set --name $FUNCTION_APP --resource-group $RG --settings `
  "AZURE_STORAGE_ACCOUNT_NAME=$DATA_STORAGE" `
  "AZURE_STORAGE_CONTAINER=documents" `
  "DOCUMENTINTELLIGENCE_ENDPOINT=$DI_ENDPOINT" `
  "AZURE_SQL_CONNECTIONSTRING=$SQL_MI_CONN" `
  "ENABLE_SQL_LOAD=true" `
  "CRITICAL_CONFIDENCE_THRESHOLD=0.70" `
  "AMOUNT_TOLERANCE=0.05" `
  "InvoiceStorage__blobServiceUri=https://$DATA_STORAGE.blob.core.windows.net" `
  "InvoiceStorage__queueServiceUri=https://$DATA_STORAGE.queue.core.windows.net" | Out-Null

# 8) Write local values file for the next steps (no secrets included).
@"
RG=$RG
LOCATION=$LOCATION
DATA_STORAGE=$DATA_STORAGE
FUNCTION_STORAGE=$FUNCTION_STORAGE
DOC_INTEL=$DOC_INTEL
DI_ENDPOINT=$DI_ENDPOINT
KEYVAULT=$KEYVAULT
SQL_SERVER=$SQL_SERVER
SQL_DB=$SQL_DB
FUNCTION_APP=$FUNCTION_APP
"@ | Set-Content -Path ".poc04-resources.txt"

Write-Host "" 
Write-Host "Azure resources created." -ForegroundColor Green
Write-Host "Next:" -ForegroundColor Yellow
Write-Host "1. Create .env from .env.example using the values in .poc04-resources.txt"
Write-Host "2. Retrieve local DI key from Key Vault only if you want key auth locally:"
Write-Host "   az keyvault secret show --vault-name $KEYVAULT --name document-intelligence-key --query value -o tsv"
Write-Host "3. Run sql/create_tables.sql as your Entra admin."
Write-Host "4. Later, after Function identity exists, run sql/create_function_identity_user.sql with <FUNCTION_APP_NAME>=$FUNCTION_APP"
