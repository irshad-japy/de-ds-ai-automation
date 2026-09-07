"""
python azure/poc_01_secure_batch_adf_adls_sql/python/upload_to_adls.py --storage-account stazdepocirshad01 --container landing --remote-path orders/2026/08/28/orders_001.csv --local-file azure/poc_01_secure_batch_adf_adls_sql/data/generated/orders_001.csv --overwrite
"""

from __future__ import annotations
import argparse
from pathlib import Path, PurePosixPath
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient

def ensure_directory(file_system_client, directory_path: str) -> None:
    current = PurePosixPath()
    for part in PurePosixPath(directory_path).parts:
        current = current / part
        directory_client = file_system_client.get_directory_client(str(current))
        try:
            directory_client.create_directory()
        except Exception as exc:  # Azure SDK uses HTTP errors for already-existing paths.
            text = str(exc).lower()
            if "pathalreadyexists" not in text and "already exists" not in text and "status: 409" not in text:
                raise

def upload(storage_account: str, container: str, remote_path: str, local_file: Path, overwrite: bool) -> None:
    if not local_file.exists():
        raise FileNotFoundError(local_file)
    account_url = f"https://{storage_account}.dfs.core.windows.net"
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    service = DataLakeServiceClient(account_url=account_url, credential=credential)
    fs = service.get_file_system_client(container)
    posix = PurePosixPath(remote_path)
    parent = str(posix.parent)
    if parent not in ("", "."):
        ensure_directory(fs, parent)
    file_client = fs.get_file_client(str(posix))
    data = local_file.read_bytes()
    file_client.upload_data(data, overwrite=overwrite)
    print("Upload successful")
    print(f"Local:  {local_file.resolve()}")
    print(f"Remote: abfss://{container}@{storage_account}.dfs.core.windows.net/{posix}")
    print(f"Bytes:  {len(data)}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a file to ADLS Gen2 using DefaultAzureCredential")
    parser.add_argument("--storage-account", required=True)
    parser.add_argument("--container", default="landing")
    parser.add_argument("--remote-path", required=True)
    parser.add_argument("--local-file", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite if the remote file already exists")
    args = parser.parse_args()

    upload(
        storage_account=args.storage_account,
        container=args.container,
        remote_path=args.remote_path,
        local_file=args.local_file,
        overwrite=args.overwrite,
    )

if __name__ == "__main__":
    main()
