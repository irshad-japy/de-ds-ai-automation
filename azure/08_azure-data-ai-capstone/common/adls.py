from __future__ import annotations

from pathlib import Path, PurePosixPath

from azure.core.exceptions import ResourceExistsError
from azure.storage.filedatalake import DataLakeServiceClient

from common.auth import get_token_credential
from common.config import Settings


def get_service_client() -> DataLakeServiceClient:
    s = Settings()
    if s.storage_connection_string:
        return DataLakeServiceClient.from_connection_string(s.storage_connection_string)
    if not s.adls_account_url:
        raise RuntimeError("Set ADLS_ACCOUNT_URL or AZURE_STORAGE_CONNECTION_STRING in .env")
    return DataLakeServiceClient(account_url=s.adls_account_url, credential=get_token_credential())


def ensure_directory(file_system_client, directory: str) -> None:
    current = ""
    for part in PurePosixPath(directory).parts:
        current = f"{current}/{part}" if current else part
        try:
            file_system_client.create_directory(current)
        except ResourceExistsError:
            pass


def upload_file(local_path: Path, remote_path: str, overwrite: bool = True) -> None:
    s = Settings()
    service = get_service_client()
    fs = service.get_file_system_client(s.adls_file_system)
    try:
        fs.create_file_system()
    except ResourceExistsError:
        pass
    remote = PurePosixPath(remote_path)
    if str(remote.parent) != ".":
        ensure_directory(fs, str(remote.parent))
    file_client = fs.get_file_client(str(remote))
    data = local_path.read_bytes()
    file_client.upload_data(data, overwrite=overwrite)
