@echo off
setlocal EnableExtensions
set "PROJECT_ROOT=%~dp0.."
set "TF_DIR=%PROJECT_ROOT%\terraform"
set "CONTAINER=poc02"

cd /d "%TF_DIR%"
for /f "usebackq delims=" %%A in (`terraform output -raw storage_account_name`) do set "STORAGE_ACCOUNT=%%A"
if "%STORAGE_ACCOUNT%"=="" (
  echo [ERROR] Could not read Terraform storage_account_name output.
  exit /b 1
)

set "ORDER_FILE=%PROJECT_ROOT%\sample_data\phase2\raw\orders\orders_batch_002_schema_evolution.csv"
set "CUSTOMER_FILE=%PROJECT_ROOT%\sample_data\phase2\raw\customers\customers_batch_002_customer_change.csv"

if not exist "%ORDER_FILE%" (
  echo [ERROR] Missing %ORDER_FILE%
  exit /b 1
)
if not exist "%CUSTOMER_FILE%" (
  echo [ERROR] Missing %CUSTOMER_FILE%
  exit /b 1
)

echo Uploading Phase-2 incremental files to %STORAGE_ACCOUNT%...

az storage fs file upload --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system "%CONTAINER%" --path "raw/orders/orders_batch_002_schema_evolution.csv" --source "%ORDER_FILE%" --overwrite true
if errorlevel 1 exit /b 1

az storage fs file upload --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system "%CONTAINER%" --path "raw/customers/customers_batch_002_customer_change.csv" --source "%CUSTOMER_FILE%" --overwrite true
if errorlevel 1 exit /b 1

echo.
echo Verify both batches are present:
az storage fs file list --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system "%CONTAINER%" --path "raw/orders" --output table
az storage fs file list --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system "%CONTAINER%" --path "raw/customers" --output table

echo.
echo [OK] Phase-2 data uploaded.
echo Next: run 06_open_phase2_job.cmd.
endlocal
