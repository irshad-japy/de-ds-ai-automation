from __future__ import annotations

import json
from typing import Iterable

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from .config import Settings


class StorageRepository:
    """Small wrapper around Blob Storage/ADLS Gen2 paths used by the POC."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.credential = DefaultAzureCredential()
        self.service = BlobServiceClient(
            account_url=settings.storage_account_url,
            credential=self.credential,
        )
        self.container = self.service.get_container_client(settings.storage_container)

    def ensure_container(self) -> None:
        try:
            self.container.create_container()
        except Exception as exc:  # ResourceExistsError can vary by SDK version
            if "ContainerAlreadyExists" not in str(exc) and "already exists" not in str(exc).lower():
                raise

    def list_blobs(self, prefix: str = "incoming/") -> Iterable[str]:
        for blob in self.container.list_blobs(name_starts_with=prefix):
            if not blob.name.endswith("/"):
                yield blob.name

    def download_bytes(self, blob_name: str) -> bytes:
        return self.container.download_blob(blob_name).readall()

    def upload_bytes(self, blob_name: str, data: bytes, overwrite: bool = True) -> None:
        self.container.upload_blob(blob_name, data, overwrite=overwrite)

    def upload_json(self, blob_name: str, payload: dict, overwrite: bool = True) -> None:
        body = json.dumps(payload, indent=2, default=str).encode("utf-8")
        self.upload_bytes(blob_name, body, overwrite=overwrite)

    def exists(self, blob_name: str) -> bool:
        return self.container.get_blob_client(blob_name).exists()
