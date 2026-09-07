# Interview Questions and Short Answers

## 1. Bronze vs Silver vs Gold?

Bronze preserves raw source data and ingestion metadata. Silver cleans, types, validates and deduplicates. Gold exposes business-ready facts, dimensions and aggregates.

## 2. Auto Loader vs batch file listing?

Auto Loader incrementally discovers files and integrates with Structured Streaming/checkpoints. A simple batch list/read typically scans the directory state each run and requires you to build your own processed-file state if you want incremental behavior.

## 3. What makes a streaming job exactly-once/idempotent in practice?

Checkpointed source progress, deterministic transformations and an idempotent/transactional sink are the main ingredients. You also need stable keys and careful retry behavior.

## 4. MERGE vs overwrite?

MERGE updates/inserts only matched/new business keys. Overwrite replaces a whole table or partition and can be much more expensive or destructive.

## 5. CDF vs CDC?

CDC is the general business pattern of capturing source changes. Delta CDF is a Delta Lake feature/API that exposes row-level changes from a table for downstream incremental processing.

## 6. SCD1 vs SCD2?

SCD1 replaces old dimension attributes with the latest value. SCD2 preserves history with effective dates and a current-row flag.

## 7. What does a checkpoint contain?

Technical streaming state such as processed offsets/files and progress metadata. It is not a copy of the business dataset.

## 8. How do small files hurt Spark?

They increase metadata/listing overhead and task scheduling overhead, often producing inefficient reads and writes.

## 9. How does Unity Catalog improve governance?

It centralizes table/storage permissions, ownership, catalog/schema organization and lineage/governance controls across Databricks data assets.

## 10. Why does this lab keep new `sales_channel` in Bronze only?

It demonstrates a controlled schema contract. Raw ingestion can accept an additive source change while curated layers change only after explicit approval.

## 11. Why use a managed identity instead of a storage key?

It avoids storing long-lived secrets in code and lets access be governed through Azure RBAC and Unity Catalog.

## 12. Why use `availableNow=True`?

It gives an incremental Structured Streaming workload that processes all files/changes available now and then stops, which is useful for scheduled batch-style pipelines.
