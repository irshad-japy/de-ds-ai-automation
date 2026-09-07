# POC-07 Azure authentication fix

## Why the old code could keep failing

The original helper had two problems:

1. `AZURE_AUTH_MODE=cli` was not implemented. Any value other than `interactive` used `DefaultAzureCredential`, so the script did not necessarily use the same identity that succeeded with `az ml workspace show`.
2. `.env` was loaded without `override=True`, so an old Windows/VS Code environment variable could continue to override the corrected project `.env` value.

The patched project fixes both behaviors.

## Recommended .env authentication

```text
AZURE_AUTH_MODE=cli
```

Then run:

```bat
az login
az account set --subscription "Azure subscription 1"
az account show -o table
poetry run python -m ml.verify_config
```

The verification output must say:

```text
Credential type: AzureCliCredential
Auth mode       : cli
```

If a browser still opens during `verify_config`, you are probably running the old project/code or an old copy of `ml/azure_utils.py`.

## Confirm which source file Python is importing

```bat
poetry run python -c "import ml.azure_utils as a; print(a.__file__)"
```

It must point to the `ml\\azure_utils.py` file inside the project you are currently running.
