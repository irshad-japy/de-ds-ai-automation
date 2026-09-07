# ADF batch pipeline

The capstone reuses the ADF concepts from POC-01 rather than forcing a second expensive orchestration stack.

## Minimal pipeline

Create an ADF pipeline named `pl_ingest_orders_to_adls` with:

1. Source: your synthetic orders landing location (local upload, Blob, SFTP, or existing lab source).
2. Sink: ADLS Gen2 `datalake/raw/orders/`.
3. Add a file-name parameter so each run can process a new file.
4. Enable retry (for example 2 retries with a short interval) on the Copy activity.
5. Add a failure path to a Web/Logic App/monitoring action if you already created one in earlier POCs.
6. Trigger manually for the POC.

For a code-first demonstration without ADF, use `poetry run python -m ingestion.batch.upload_orders`. The capstone goal is integration; either path can be shown in the five-minute demo.
