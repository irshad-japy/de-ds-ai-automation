from __future__ import annotations

import os
from pathlib import Path

import mlflow
from dotenv import load_dotenv

from .common import PROJECT_ROOT

ENV_FILE = PROJECT_ROOT / ".env"


def load_project_env(*, override: bool = True) -> Path:
    """Load the project .env file.

    override=True is intentional for this beginner POC so the values in the
    project's .env are the effective values even when an older Windows/VS Code
    environment variable is still present in the shell.
    """
    load_dotenv(dotenv_path=ENV_FILE, override=override)
    return ENV_FILE


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is empty. Copy .env.example to .env and fill your Azure workspace values."
        )
    return value


def get_workspace_name() -> str:
    """Support both workspace env-var spellings used during the POC."""
    value = (
        os.getenv("AZUREML_WORKSPACE_NAME", "").strip()
        or os.getenv("AZURE_ML_WORKSPACE_NAME", "").strip()
    )
    if not value:
        raise RuntimeError(
            "AZUREML_WORKSPACE_NAME (or AZURE_ML_WORKSPACE_NAME) is empty. "
            "Set it in the project .env file."
        )
    return value


def get_credential():
    """Return the credential requested by AZURE_AUTH_MODE.

    Supported modes:
      cli         -> AzureCliCredential (recommended for this local Windows POC)
      interactive -> InteractiveBrowserCredential
      default     -> DefaultAzureCredential

    The original project treated every non-interactive value as
    DefaultAzureCredential. That meant AZURE_AUTH_MODE=cli did not actually use
    the Azure CLI login. This implementation handles the modes explicitly.
    """
    from azure.identity import (
        AzureCliCredential,
        DefaultAzureCredential,
        InteractiveBrowserCredential,
    )

    load_project_env()
    tenant_id = os.getenv("AZURE_TENANT_ID", "").strip() or None
    subscription_id = _required("AZURE_SUBSCRIPTION_ID")
    mode = os.getenv("AZURE_AUTH_MODE", "cli").strip().lower()

    if mode == "cli":
        kwargs: dict[str, str] = {"subscription": subscription_id}
        if tenant_id:
            kwargs["tenant_id"] = tenant_id
        return AzureCliCredential(**kwargs)

    if mode in {"interactive", "browser"}:
        kwargs = {"tenant_id": tenant_id} if tenant_id else {}
        return InteractiveBrowserCredential(**kwargs)

    if mode == "default":
        kwargs = {"tenant_id": tenant_id} if tenant_id else {}
        return DefaultAzureCredential(
            exclude_interactive_browser_credential=True,
            **kwargs,
        )

    raise ValueError(
        f"Unsupported AZURE_AUTH_MODE={mode!r}. "
        "Use 'cli', 'interactive', or 'default'."
    )


def get_ml_client():
    from azure.ai.ml import MLClient

    load_project_env()
    return MLClient(
        credential=get_credential(),
        subscription_id=_required("AZURE_SUBSCRIPTION_ID"),
        resource_group_name=_required("AZURE_RESOURCE_GROUP"),
        workspace_name=get_workspace_name(),
    )


def get_workspace(client=None):
    """Retrieve the configured Azure ML workspace using an existing/new client."""
    if client is None:
        client = get_ml_client()
    return client.workspaces.get(get_workspace_name())


def configure_mlflow_for_azure(client=None) -> str:
    """Point MLflow at this Azure ML workspace and return the tracking URI."""
    if client is None:
        client = get_ml_client()
    workspace = get_workspace(client)
    uri = workspace.mlflow_tracking_uri
    if not uri:
        raise RuntimeError("Azure ML workspace did not return an MLflow tracking URI.")
    mlflow.set_tracking_uri(uri)
    return uri


def configure_mlflow_local() -> str:
    from .common import MLRUNS_DIR, ensure_dirs

    ensure_dirs()
    uri = MLRUNS_DIR.resolve().as_uri()
    mlflow.set_tracking_uri(uri)
    return uri


def configure_tracking(mode: str) -> str:
    mode = mode.lower().strip()
    if mode == "azure":
        return configure_mlflow_for_azure()
    if mode == "local":
        return configure_mlflow_local()
    raise ValueError("tracking mode must be 'local' or 'azure'")
