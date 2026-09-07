$ErrorActionPreference = "Stop"
Write-Host "POC-08 Poetry bootstrap" -ForegroundColor Cyan
py -3.12 --version
poetry --version
poetry env use 3.12
poetry install
poetry run python -m scripts.verify_config --profile local
poetry run pytest
Write-Host "Bootstrap completed." -ForegroundColor Green
