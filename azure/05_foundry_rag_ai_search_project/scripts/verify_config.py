from __future__ import annotations

from rag.config import settings


def ok(message: str) -> None:
    print(f"[OK] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")


def main() -> None:
    errors = []

    if settings.azure_search_endpoint.startswith("https://") and ".search.windows.net" in settings.azure_search_endpoint:
        ok("AZURE_SEARCH_ENDPOINT configured")
    else:
        errors.append("AZURE_SEARCH_ENDPOINT must be an https://*.search.windows.net endpoint")
        fail(errors[-1])

    if settings.search_auth_mode == "key":
        if settings.azure_search_admin_key and "PASTE_" not in settings.azure_search_admin_key:
            ok("Azure AI Search key authentication configured")
        else:
            errors.append("AZURE_SEARCH_ADMIN_KEY missing/placeholder for SEARCH_AUTH_MODE=key")
            fail(errors[-1])
    elif settings.search_auth_mode == "entra":
        ok("Azure AI Search Entra authentication selected; run az login before Azure calls")
    else:
        errors.append("SEARCH_AUTH_MODE must be key or entra")
        fail(errors[-1])

    if settings.foundry_openai_base_url.startswith("https://") and "/openai/v1" in settings.foundry_openai_base_url:
        ok("FOUNDRY_OPENAI_BASE_URL configured")
    else:
        errors.append("FOUNDRY_OPENAI_BASE_URL must be an https endpoint containing /openai/v1")
        fail(errors[-1])

    if settings.foundry_auth_mode == "key":
        if settings.foundry_api_key and "PASTE_" not in settings.foundry_api_key:
            ok("Foundry key authentication configured")
        else:
            errors.append("FOUNDRY_API_KEY missing/placeholder for FOUNDRY_AUTH_MODE=key")
            fail(errors[-1])
    elif settings.foundry_auth_mode == "entra":
        ok("Foundry Entra authentication selected; run az login before model calls")
    else:
        errors.append("FOUNDRY_AUTH_MODE must be key or entra")
        fail(errors[-1])

    if settings.embedding_dimensions > 0:
        ok(f"Embedding dimensions: {settings.embedding_dimensions}")
    else:
        errors.append("EMBEDDING_DIMENSIONS must be positive")
        fail(errors[-1])

    if settings.chunk_overlap_tokens >= settings.chunk_size_tokens:
        errors.append("CHUNK_OVERLAP_TOKENS must be less than CHUNK_SIZE_TOKENS")
        fail(errors[-1])
    else:
        ok(
            f"Chunking configured: size={settings.chunk_size_tokens}, overlap={settings.chunk_overlap_tokens}"
        )

    if errors:
        print(f"\nConfiguration validation FAILED with {len(errors)} issue(s).")
        raise SystemExit(1)

    print("\nConfiguration validation passed.")


if __name__ == "__main__":
    main()
