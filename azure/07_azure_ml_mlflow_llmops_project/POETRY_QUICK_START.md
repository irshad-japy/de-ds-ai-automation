# POC-07 Poetry Quick Start — Windows

Run these commands from the project root.

## 1. Verify prerequisites

```bat
poetry --version
py -3.12 --version
```

## 2. Create/select the Poetry environment

```bat
poetry env use 3.12
```

The included `poetry.toml` makes Poetry create/use `.venv` inside this project.

## 3. Install dependencies

```bat
poetry install
```

On the first successful install, Poetry will generate `poetry.lock`.

## 4. Verify

```bat
poetry env info
poetry run python --version
poetry run python -c "import mlflow, sklearn, pandas; print('Poetry environment OK')"
```

## 5. Recommended: run without activating

```bat
poetry run python -m ml.generate_data
poetry run python -m ml.train --tracking local
poetry run python -m ml.compare_runs
poetry run python -m ml.score --tracking local
poetry run python -m ml.verify_poc --tracking local
poetry run pytest -q
```

Or run all local checks:

```bat
scripts\run_local_poetry_windows.bat
```

## 6. Optional: activate `.venv`

### CMD

```bat
call .venv\Scripts\activate.bat
```

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation:

```bat
python -m ml.generate_data
python -m ml.train --tracking local
```

Exit:

```bat
deactivate
```

## 7. Azure POC commands after `.env` is configured

```bat
poetry run python -m ml.verify_config
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
