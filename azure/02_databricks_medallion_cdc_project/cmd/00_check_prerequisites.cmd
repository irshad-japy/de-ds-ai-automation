@echo off
setlocal

echo ============================================================
echo POC-02 prerequisite check
echo ============================================================

where az >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Azure CLI ^(az^) was not found in PATH.
  echo Install Azure CLI, reopen Command Prompt, and rerun this file.
  exit /b 1
)

where terraform >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Terraform was not found in PATH.
  echo Install Terraform, reopen Command Prompt, and rerun this file.
  exit /b 1
)

echo.
echo Azure CLI:
az version --output table

echo.
echo Terraform:
terraform version

echo.
echo Current Azure login:
az account show --output table
if errorlevel 1 (
  echo.
  echo [INFO] You are not logged in. Run: az login
)

echo.
echo [OK] Prerequisite check finished.
endlocal
