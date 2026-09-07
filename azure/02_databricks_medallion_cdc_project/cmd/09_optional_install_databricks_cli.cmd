@echo off
setlocal
where winget >nul 2>&1 || (
  echo [ERROR] winget is not available. Install Databricks CLI manually if you want CLI job execution.
  exit /b 1
)
echo Searching for Databricks CLI...
winget search databricks
echo.
echo Installing official Databricks CLI package...
winget install Databricks.DatabricksCLI

echo.
echo Reopen Command Prompt after installation, then run: databricks -v
endlocal
