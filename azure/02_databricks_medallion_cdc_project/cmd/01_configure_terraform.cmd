@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "PROJECT_ROOT=%~dp0.."
set "TF_DIR=%PROJECT_ROOT%\terraform"

where az >nul 2>&1 || (
  echo [ERROR] Azure CLI is not installed or not in PATH.
  exit /b 1
)

az account show >nul 2>&1
if errorlevel 1 (
  echo Logging in to Azure...
  az login
  if errorlevel 1 exit /b 1
)

echo.
echo Available subscriptions:
az account list --query "[].{Name:name,SubscriptionId:id,State:state}" --output table

echo.
set "SUBSCRIPTION_ID="
set /p "SUBSCRIPTION_ID=Enter the Subscription ID to use: "
if "%SUBSCRIPTION_ID%"=="" (
  echo [ERROR] Subscription ID cannot be empty.
  exit /b 1
)

az account set --subscription "%SUBSCRIPTION_ID%"
if errorlevel 1 exit /b 1

set "REGION=centralindia"
set /p "REGION_INPUT=Azure region [centralindia]: "
if not "%REGION_INPUT%"=="" set "REGION=%REGION_INPUT%"

> "%TF_DIR%\terraform.tfvars" (
  echo subscription_id = "%SUBSCRIPTION_ID%"
  echo location = "%REGION%"
  echo resource_group_name = "rg-azde-poc02"
  echo storage_account_prefix = "stazdepoc02"
  echo container_name = "poc02"
  echo access_connector_name = "ac-azde-poc02"
  echo databricks_workspace_name = "dbw-azde-poc02"
  echo catalog_name = "azde_poc"
  echo storage_credential_name = "poc02_storage_cred"
  echo external_location_name = "poc02_ext"
  echo job_num_workers = 1
)

echo.
echo [OK] Created: %TF_DIR%\terraform.tfvars
echo Active subscription:
az account show --query "{Name:name,Id:id,Tenant:tenantId}" --output table

echo.
echo Next: run 02_terraform_apply.cmd
endlocal
