# Poetry setup on Windows

This project uses Poetry instead of a `pip install -r requirements.txt` workflow.

## Recommended commands

```powershell
py -3.12 --version
poetry --version
poetry env use 3.12
poetry install
poetry env info
poetry run python --version
```

You do **not** have to manually activate the venv. The safest beginner pattern is:

```powershell
poetry run python -m scripts.smoke_test
```

## If you want an activated shell

Poetry 2.x no longer guarantees that `poetry shell` is installed by default. Use either:

```powershell
poetry env activate
```

Copy/run the activation command Poetry prints, or in PowerShell:

```powershell
Invoke-Expression (poetry env activate)
```

Optional legacy-style shell plugin:

```powershell
poetry self add poetry-plugin-shell
poetry shell
```

## Optional feature groups

```powershell
poetry install --with sql
poetry install --with ml
poetry install --with functions
poetry install --with sql,ml,functions
```
