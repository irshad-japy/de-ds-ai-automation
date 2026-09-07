from __future__ import annotations

from azure.core.exceptions import ResourceNotFoundError
from rag.clients import get_search_index_client
from rag.config import settings


def main() -> None:
    client = get_search_index_client()
    try:
        client.delete_index(settings.azure_search_index_name)
        print(f"Deleted index: {settings.azure_search_index_name}")
    except ResourceNotFoundError:
        print(f"Index does not exist: {settings.azure_search_index_name}")


if __name__ == "__main__":
    main()
