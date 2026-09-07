@echo off
setlocal
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%\terraform"
for /f "usebackq delims=" %%A in (`terraform output -raw phase1_job_url`) do set "JOB_URL=%%A"
if "%JOB_URL%"=="" (
  echo [ERROR] phase1_job_url output is empty.
  exit /b 1
)
echo Opening Phase-1 Databricks Job:
echo %JOB_URL%
start "" "%JOB_URL%"
echo.
echo In Databricks: click Run now and wait for setup -^> bronze -^> silver -^> gold to complete.
endlocal
