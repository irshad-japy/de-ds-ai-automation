from __future__ import annotations

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

from common.config import env


def get_token_credential():
    """Return a local-friendly Azure token credential.

    AZURE_AUTH_MODE=browser is useful for beginners who do not yet have Azure CLI.
    AZURE_AUTH_MODE=default uses DefaultAzureCredential and works well with `az login`,
    managed identity, workload identity, environment credentials, and other standard flows.
    """
    mode = env("AZURE_AUTH_MODE", "browser").lower()
    tenant_id = env("AZURE_TENANT_ID") or None
    if mode == "browser":
        return InteractiveBrowserCredential(tenant_id=tenant_id)
    return DefaultAzureCredential()
