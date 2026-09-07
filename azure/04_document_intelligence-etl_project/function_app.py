from __future__ import annotations

import json
import logging

import azure.functions as func

from src.config import get_settings
from src.pipeline import InvoicePipeline

app = func.FunctionApp()

@app.function_name(name="InvoiceBlobTrigger")
@app.blob_trigger(
    arg_name="inputblob",
    path="documents/incoming/{name}",
    connection="InvoiceStorage",
)
def invoice_blob_trigger(inputblob: func.InputStream):
    """Optional automation layer. The local batch runner is easier for your first successful POC run."""
    source_blob = inputblob.name
    # Azure Functions may report '<container>/incoming/file.pdf'.
    if source_blob.startswith("documents/"):
        source_blob = source_blob[len("documents/") :]

    logging.info("Invoice trigger received blob: %s (%s bytes)", source_blob, inputblob.length)
    settings = get_settings()
    pipeline = InvoicePipeline(settings)
    result = pipeline.process_bytes(inputblob.read(), source_blob=source_blob)
    logging.info("Invoice pipeline result: %s", json.dumps(result, default=str))
