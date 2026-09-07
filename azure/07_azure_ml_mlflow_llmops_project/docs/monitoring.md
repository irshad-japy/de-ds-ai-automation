# Monitoring plan

The source POC asks for scoring latency, errors, prediction distribution, feature drift, and data freshness.

## Minimum production signals
- **Latency:** request/job latency and per-row scoring duration.
- **Errors:** failed endpoint calls, failed batch mini-batches, schema/type failures.
- **Prediction distribution:** mean/p95 `risk_score`, delayed-class rate, sudden shifts.
- **Feature drift:** compare numeric/categorical feature distributions with training reference data.
- **Data freshness:** time since the newest source shipment/feature snapshot.

`ml.score` writes `outputs/scoring_metrics.json` with local scoring latency and prediction-distribution values. Azure endpoint telemetry can be viewed through Azure Monitor/Application Insights where configured.

Pipeline monitoring asks, “Did the data/job execute correctly?” Model monitoring additionally asks, “Is the model still receiving representative data and producing healthy predictions?”
