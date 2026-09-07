# POC-07 Runbook — Poetry First

Run all commands from the project root on Windows.

## 1. Create/install the Poetry environment

```bat
poetry --version
py -3.12 --version
poetry env use 3.12
poetry install
poetry env info
poetry run python --version
```

The included `poetry.toml` keeps the environment in `.venv`.

Recommended: do not activate it; run every command with `poetry run`.

Optional CMD activation:

```bat
call .venv\Scripts\activate.bat
```

Optional PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 2. Local verification

```bat
poetry run python -m ml.generate_data
poetry run python -m ml.train --tracking local
poetry run python -m ml.compare_runs
poetry run python -m ml.score --tracking local
poetry run python -m ml.verify_poc --tracking local
poetry run pytest -q
```

Or:

```bat
scripts\run_local_poetry_windows.bat
```

## 3. Azure configuration

Create `.env` from `.env.example`, fill the subscription/resource-group/workspace values, then:

```bat
poetry run python -m ml.verify_config
```

## 4. Azure MLflow + registry flow

```bat
poetry run python -m ml.generate_data
poetry run python -m ml.register_data
poetry run python -m ml.train --tracking azure
poetry run python -m ml.compare_runs
poetry run python -m ml.register_model --tracking azure
poetry run python -m ml.score --tracking azure
poetry run python -m ml.verify_poc --tracking azure --check-registry
```

Or:

```bat
scripts\run_azure_tracking_poetry_windows.bat
```

## 5. Optional batch deployment

```bat
poetry run python azure\batch\deploy_batch.py
poetry run python azure\batch\invoke_batch.py
poetry run python azure\batch\cleanup_batch.py
```

Always run cleanup after batch validation.
