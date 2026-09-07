@echo off
setlocal
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%\terraform"
for /f "usebackq delims=" %%A in (`terraform output -raw phase2_job_url`) do set "JOB_URL=%%A"
if "%JOB_URL%"=="" (
  echo [ERROR] phase2_job_url output is empty.
  exit /b 1
)
echo Opening Phase-2 Databricks Job:
echo %JOB_URL%
start "" "%JOB_URL%"
echo.
echo Click Run now.
echo IMPORTANT: Auto Loader addNewColumns can intentionally stop the first Phase-2 run after discovering sales_channel.
echo If bronze_incremental shows that expected schema-evolution restart behavior, click Run now again.
endlocal
