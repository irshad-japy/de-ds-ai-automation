# Poetry setup for POC-07

This project uses Poetry as the primary dependency and virtual-environment manager.

## Files

- `pyproject.toml` — Python version and project dependencies.
- `poetry.toml` — sets `virtualenvs.in-project = true`, so the environment is created as `.venv` in this folder.
- `requirements.txt` — legacy/fallback only; it is not the recommended setup.

## Windows CMD — recommended flow

```bat
cd C:\path\to\POC_07_AZURE_ML_MLFLOW_LLMOPS_PROJECT
poetry --version
py -3.12 --version
poetry env use 3.12
poetry install
poetry env info
poetry run python --version
```

Run without activation:

```bat
poetry run python -m ml.generate_data
poetry run python -m ml.train --tracking local
```

## Windows CMD — optional activation

```bat
call .venv\Scripts\activate.bat
python --version
```

After activation, plain Python commands work:

```bat
python -m ml.generate_data
python -m ml.train --tracking local
```

Exit:

```bat
deactivate
```

## PowerShell — optional activation

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell execution policy blocks `Activate.ps1`, use `poetry run ...` instead; activation is not required.

## Useful Poetry commands

```bat
poetry env info
poetry env info --path
poetry env list
poetry show
poetry show --tree
poetry run python --version
poetry run pytest -q
```

To recreate the project environment:

```bat
poetry env remove --all
poetry env use 3.12
poetry install
```
