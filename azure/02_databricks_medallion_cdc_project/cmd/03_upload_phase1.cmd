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

set "ORDER_FILE=%PROJECT_ROOT%\sample_data\phase1\raw\orders\orders_batch_001.csv"
set "CUSTOMER_FILE=%PROJECT_ROOT%\sample_data\phase1\raw\customers\customers_batch_001.csv"

if not exist "%ORDER_FILE%" (
  echo [ERROR] Missing %ORDER_FILE%
  exit /b 1
)
if not exist "%CUSTOMER_FILE%" (
  echo [ERROR] Missing %CUSTOMER_FILE%
  exit /b 1
)

echo Storage account: %STORAGE_ACCOUNT%
echo Uploading Phase-1 files using your Azure login...

az storage fs file upload --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system "%CONTAINER%" --path "raw/orders/orders_batch_001.csv" --source "%ORDER_FILE%" --overwrite true
if errorlevel 1 goto :upload_error

az storage fs file upload --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system "%CONTAINER%" --path "raw/customers/customers_batch_001.csv" --source "%CUSTOMER_FILE%" --overwrite true
if errorlevel 1 goto :upload_error

echo.
echo Verify ADLS files:
az storage fs file list --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system "%CONTAINER%" --path "raw/orders" --output table
az storage fs file list --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system "%CONTAINER%" --path "raw/customers" --output table

echo.
echo [OK] Phase-1 data uploaded.
echo Next: run 04_open_phase1_job.cmd, click Run now, then execute sql\validation_queries.sql.
exit /b 0

:upload_error
echo.
echo [ERROR] ADLS upload failed.
echo Terraform grants your login Storage Blob Data Contributor. If Azure has not applied the data-plane permission yet, confirm the active subscription and rerun this script.
exit /b 1
