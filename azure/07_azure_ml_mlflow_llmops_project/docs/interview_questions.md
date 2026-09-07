# Interview questions and concise answers

1. **MLflow tracking vs model registry?** Tracking stores experiment runs, parameters, metrics, artifacts and lineage. The registry manages named, versioned model assets intended for lifecycle/deployment.
2. **Batch vs online inference?** Batch is asynchronous/high-throughput and suits non-low-latency workloads. Online inference serves low-latency request/response APIs and typically costs more while provisioned.
3. **What is data leakage?** Information unavailable at prediction time enters training features, making validation unrealistically good.
4. **How do you version data and models?** Give immutable data references/fingerprints and register model versions that point back to source run, code version, parameters and metrics.
5. **Model monitoring vs pipeline monitoring?** Pipeline monitoring checks execution/availability/data movement; model monitoring checks prediction quality proxies, drift, score distribution and data relevance/freshness.
6. **How would a Data Engineer support ML reproducibility?** Version curated inputs, enforce schemas, preserve lineage, make transformations deterministic, orchestrate repeatable jobs, and retain data/model metadata.
