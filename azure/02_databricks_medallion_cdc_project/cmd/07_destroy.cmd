@echo off
setlocal
set "PROJECT_ROOT=%~dp0.."
set "TF_DIR=%PROJECT_ROOT%\terraform"
cd /d "%TF_DIR%"

if not exist terraform.tfstate (
  echo [WARNING] No terraform.tfstate found in %TF_DIR%.
  echo Nothing can be safely destroyed by this local Terraform state.
  exit /b 1
)

echo ============================================================
echo POC-02 DESTRUCTIVE CLEANUP
echo ============================================================
echo This will delete the Terraform-managed Databricks jobs/notebooks,
echo Unity Catalog POC catalog/external objects, Databricks workspace,
echo ADLS data, Access Connector, and resource group resources.
echo.
set /p "CONFIRM=Type DESTROY to continue: "
if /I not "%CONFIRM%"=="DESTROY" (
  echo Cancelled.
  exit /b 0
)

echo.
terraform plan -destroy -out=poc02-destroy.tfplan
if errorlevel 1 exit /b 1

echo.
terraform apply poc02-destroy.tfplan
if errorlevel 1 exit /b 1

echo.
echo [OK] Terraform destroy completed.
echo Verify with: az group show --name rg-azde-poc02
endlocal
