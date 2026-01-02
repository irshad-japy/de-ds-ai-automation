"""
python -m app.services.upload_on_s3
"""


from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


def generate_presigned_url(s3_client, bucket, key, expires_seconds=7 * 24 * 3600):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_seconds,
    )

def upload_file_and_get_presigned_url(
    file_path: str | Path,
    bucket: str,
    key_prefix: str = "",
    expires_seconds: int = 7 * 24 * 3600,
) -> dict:
    file_path = Path(file_path).expanduser().resolve()
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    s3 = boto3.client("s3")

    prefix = key_prefix.strip().lstrip("/")
    ext = file_path.suffix
    base = file_path.stem
    unique_name = f"{base}-{uuid.uuid4().hex}{ext}"
    key = f"{prefix}/{unique_name}" if prefix else unique_name

    content_type, _ = mimetypes.guess_type(str(file_path))
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    try:
        with open(file_path, "rb") as f:
            s3.upload_fileobj(f, bucket, key, ExtraArgs=extra_args or None)

        presigned_url = generate_presigned_url(
            s3_client=s3,
            bucket=bucket,
            key=key,
            expires_seconds=expires_seconds,
        )

        return {
            "bucket": bucket,
            "key": key,
            "s3_uri": f"s3://{bucket}/{key}",
            "presigned_url": presigned_url,
            "expires_seconds": expires_seconds,
        }

    except ClientError as e:
        raise RuntimeError(f"S3 upload failed: {e}") from e


def main(file_path: str, bucket: str, prefix: str, expires_seconds: int):
    result = upload_file_and_get_presigned_url(
        file_path=file_path,
        bucket=bucket,
        key_prefix=prefix,              # ✅ FIXED
        expires_seconds=expires_seconds,
    )

    print("\n✅ Upload successful")
    print(f"S3 URI:        {result['s3_uri']}")
    print(f"Expires (sec): {result['expires_seconds']}")
    print(f"Presigned URL: {result['presigned_url']}\n")

if __name__ == "__main__":
    file_path = r"C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/thumbnail/thumb_7f50d3a2_seed_42.png"  # ✅ FIXED (raw string)
    bucket = "tge-nihau-bucket"
    prefix = "irshad/temp"
    expires_seconds = 604800

    main(file_path, bucket, prefix, expires_seconds)
