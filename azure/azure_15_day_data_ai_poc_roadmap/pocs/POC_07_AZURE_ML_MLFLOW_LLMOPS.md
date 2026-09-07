# POC-07 — Azure Machine Learning + MLflow + LLMOps/MLOps

## Objective

Show a production-minded ML workflow that complements Data Engineering skills.

Use a simple, explainable problem: **predict whether a synthetic shipment will be delayed**.

## Services

- Azure Machine Learning
- MLflow
- Azure Storage/ADLS
- optional Azure ML managed compute
- model registry
- batch or managed online endpoint
- Azure Monitor / Application Insights where applicable
- Git/YAML CI concepts

## Cost guardrails

- Use a tiny dataset.
- Prefer local training + Azure ML tracking if practical.
- If Azure compute is used, choose the smallest suitable option and delete it immediately after the run.
- Delete managed online endpoints after validation because endpoints can incur ongoing cost.

## Steps

### 1. Create synthetic training data

Features:

```text
origin_region
destination_region
carrier
distance_km
order_hour
weekday
priority
historical_delay_rate
```

Label:

```text
is_delayed
```

### 2. Define train/validation split

Prevent leakage: do not use a feature that is known only after the shipment is delayed.

### 3. Create Azure ML workspace

Connect storage.

### 4. Track experiment with MLflow

Log:

```text
parameters
metrics
model
feature list
code version
```

### 5. Train two simple models

Example:

- logistic regression baseline
- tree-based model

Compare metrics.

### 6. Register the selected model

Record:

- model version
- training dataset version/reference
- metric
- limitations

### 7. Deployment

Choose one:

**Option A — Batch scoring:** cheapest and closest to many data-engineering workloads.

**Option B — Managed online endpoint:** useful for API serving, but delete immediately after demo.

### 8. Monitoring concept

Track:

- scoring latency
- errors
- prediction distribution
- feature drift concept
- data freshness

### 9. Reproducibility

A new clone of the repo should be able to:

1. create the environment;
2. generate data;
3. train;
4. log to MLflow;
5. produce the same class of results.

### 10. Connect to the AI portfolio

Use the model output as one tool/feature in the capstone:

```text
risk_score = shipment delay probability
```

The agent may explain the risk score, but must not claim causal certainty.

## Validation

- Two experiments logged.
- Metrics can be compared.
- Selected model registered.
- One scoring path works.
- Endpoint/compute deleted after testing.
- Leakage review documented.

## GitHub artifacts

```text
ml/
  generate_data.py
  train.py
  score.py
  requirements.txt
docs/
  experiment_results.md
  model_card.md
  data_leakage_check.md
```

## Interview questions

1. MLflow tracking vs model registry?
2. Batch vs online inference?
3. What is data leakage?
4. How do you version data and models?
5. How is model monitoring different from pipeline monitoring?
6. How would a Data Engineer support ML reproducibility?

## CV text — USE ONLY AFTER COMPLETION

- Built an Azure Machine Learning workflow with MLflow experiment tracking, model comparison, registration and reproducible shipment-delay scoring.
- Documented feature leakage controls, model metadata, batch/endpoint deployment trade-offs and monitoring requirements.
- Integrated curated data-engineering outputs with an ML scoring layer suitable for downstream analytics and AI-agent consumption.
