# Performance and Tuning Notes

This POC intentionally uses tiny data. The objective is to practice what to inspect, not to claim benchmark results.

## Inspect now

- `df.rdd.getNumPartitions()`
- `df.explain("formatted")`
- `DESCRIBE DETAIL <table>`
- `DESCRIBE HISTORY <table>`
- Jobs run duration and task metrics

## Questions for 100 GB / 1 TB scale

1. Are source files extremely small? If yes, reduce small-file creation and consider compaction/optimized writes supported by the platform.
2. Does the query filter on selective columns? Review data skipping/clustering capabilities available for the table/runtime.
3. Is manual partitioning useful? Do not partition on a high-cardinality ID simply because it exists.
4. Are joins causing large shuffles? Review join strategy, broadcast suitability and skew.
5. Are there too many shuffle partitions or too few for the workload?
6. Can the pipeline process incrementally instead of scanning full history?
7. Is the compute oversized or undersized for the SLA?
8. Can job/serverless compute reduce idle cost?
9. Are table maintenance and retention policies appropriate?

## Small-files interview point

Many tiny files increase metadata/listing overhead and can create many Spark tasks. The correct remedy depends on the ingestion and table-layout strategy; do not solve every case by adding partitions.
