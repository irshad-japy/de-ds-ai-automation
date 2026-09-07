@echo off
setlocal

where poetry >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Poetry is not available in PATH.
  echo Install Poetry first, reopen CMD, then rerun this script.
  exit /b 1
)

echo [1/4] Poetry version
poetry --version || exit /b 1

echo [2/4] Select Python 3.12
poetry env use 3.12 || exit /b 1

echo [3/4] Install POC dependencies from pyproject.toml
poetry install || exit /b 1

echo [4/4] Verify Poetry environment
poetry env info || exit /b 1
poetry run python --version || exit /b 1

echo.
echo [SUCCESS] Poetry environment is ready.
echo You can run commands without activation, for example:
echo   poetry run python -m ml.generate_data
echo.
echo Because poetry.toml sets virtualenvs.in-project=true, the environment is .venv.
echo To activate in CMD:
echo   call .venv\Scripts\activate.bat
