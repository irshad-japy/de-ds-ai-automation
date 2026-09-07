@echo off
setlocal
set "PROJECT_ROOT=%~dp0.."
set "TF_DIR=%PROJECT_ROOT%\terraform"
cd /d "%TF_DIR%"

if not exist terraform.tfvars (
  echo [ERROR] terraform.tfvars does not exist.
  echo Run ..\cmd\01_configure_terraform.cmd first.
  exit /b 1
)

where terraform >nul 2>&1 || (
  echo [ERROR] Terraform is not in PATH.
  exit /b 1
)

where az >nul 2>&1 || (
  echo [ERROR] Azure CLI is not in PATH.
  exit /b 1
)

az account show >nul 2>&1 || (
  echo [ERROR] Azure CLI is not logged in. Run az login.
  exit /b 1
)

echo ============================================================
echo terraform init
echo ============================================================
terraform init -upgrade
if errorlevel 1 exit /b 1

echo ============================================================
echo terraform fmt + validate
echo ============================================================
terraform fmt -recursive
terraform validate
if errorlevel 1 exit /b 1

echo ============================================================
echo terraform plan
echo ============================================================
terraform plan -out=poc02.tfplan
if errorlevel 1 exit /b 1

echo ============================================================
echo terraform apply
echo ============================================================
terraform apply poc02.tfplan
if errorlevel 1 (
  echo.
  echo [ERROR] Terraform apply failed.
  echo Check README.md troubleshooting. If the failure is only Azure RBAC propagation or a newly created Databricks workspace API readiness issue, rerun this same script.
  exit /b 1
)

echo.
echo ============================================================
echo Terraform outputs
echo ============================================================
terraform output

echo.
echo [OK] Infrastructure and Databricks assets were provisioned.
echo Next: run 03_upload_phase1.cmd
endlocal
