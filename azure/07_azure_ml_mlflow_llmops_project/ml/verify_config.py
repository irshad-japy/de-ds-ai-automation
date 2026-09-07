from __future__ import annotations

import argparse
import os
import sys

from .azure_utils import (
    ENV_FILE,
    configure_mlflow_for_azure,
    get_credential,
    get_ml_client,
    get_workspace,
    get_workspace_name,
    load_project_env,
)


def _mask_subscription(value: str) -> str:
    value = value.strip()
    if len(value) < 12:
        return value
    return f"{value[:8]}...{value[-4:]}"


def _print_effective_config() -> None:
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "").strip()
    print("\nEffective configuration used by Python:")
    print(f"  .env file       : {ENV_FILE}")
    print(f"  Subscription ID : {_mask_subscription(subscription_id)}")
    print(f"  Resource group  : {os.getenv('AZURE_RESOURCE_GROUP', '').strip()}")
    print(f"  Workspace       : {get_workspace_name()}")
    print(f"  Tenant ID       : {os.getenv('AZURE_TENANT_ID', '').strip() or '<Azure CLI/default>'}")
    print(f"  Auth mode       : {os.getenv('AZURE_AUTH_MODE', 'cli').strip().lower()}")


def _print_azure_error(exc: Exception) -> None:
    print("\n[FAIL] Azure verification failed.")
    print(f"Exception type: {type(exc).__name__}")

    status_code = getattr(exc, "status_code", None)
    error = getattr(exc, "error", None)
    error_code = getattr(error, "code", None) if error is not None else None
    message = getattr(error, "message", None) if error is not None else None

    if status_code is not None:
        print(f"Status code   : {status_code}")
    if error_code:
        print(f"Error code    : {error_code}")
    if message:
        print(f"Azure message : {message}")
    else:
        print(f"Message       : {exc}")

    print("\nRecommended checks:")
    print("  1. az account show -o table")
    print("  2. az ml workspace show --name <workspace> --resource-group <rg> -o table")
    print("  3. Confirm AZURE_AUTH_MODE=cli in the project .env")
    print("  4. Run this command again from the project root")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-azure",
        action="store_true",
        help="Only validate local environment variables/files.",
    )
    args = parser.parse_args()

    # Important: project .env wins over stale shell/VS Code variables.
    load_project_env(override=True)

    names = ["AZURE_SUBSCRIPTION_ID", "AZURE_RESOURCE_GROUP"]
    missing = [name for name in names if not os.getenv(name, "").strip()]
    try:
        get_workspace_name()
    except RuntimeError:
        missing.append("AZUREML_WORKSPACE_NAME")

    if missing:
        print(f"[FAIL] Missing values in .env: {', '.join(missing)}")
        sys.exit(2)

    print("[OK] Required .env settings are present.")
    _print_effective_config()

    if args.no_azure:
        print("\n[OK] Local configuration validation passed (--no-azure).")
        return

    try:
        print("\n[1/4] Building Azure credential...")
        credential = get_credential()
        print(f"[OK] Credential type: {type(credential).__name__}")

        print("\n[2/4] Testing Azure Resource Manager authentication...")
        credential.get_token("https://management.azure.com/.default")
        print("[OK] Azure authentication succeeded.")

        print("\n[3/4] Looking up the configured Azure ML workspace...")
        client = get_ml_client()
        workspace = get_workspace(client)
        print(f"[OK] Connected to Azure ML workspace: {workspace.name}")
        print(f"[OK] Location: {workspace.location}")
        print(f"[OK] Resource group: {os.getenv('AZURE_RESOURCE_GROUP', '').strip()}")
        print(f"[OK] Provisioning state: {getattr(workspace, 'provisioning_state', '<not returned>')}")

        print("\n[4/4] Discovering Azure ML MLflow tracking URI...")
        tracking_uri = configure_mlflow_for_azure(client=client)
        print(f"[OK] MLflow tracking URI: {tracking_uri}")

    except Exception as exc:  # diagnostic script: render SDK failures clearly
        _print_azure_error(exc)
        sys.exit(1)

    print("\n[SUCCESS] Azure ML workspace + MLflow configuration verified.")
    print("Next: poetry run python -m ml.register_data")


if __name__ == "__main__":
    main()
