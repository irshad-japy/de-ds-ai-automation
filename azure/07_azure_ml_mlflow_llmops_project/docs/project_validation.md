# Project build validation

Validation performed while assembling this ZIP:

- Python source tree compiled successfully with `compileall`.
- Synthetic data generation executed successfully.
- Unit tests passed for deterministic generation and the eight-feature leakage contract.
- Logistic regression and random-forest pipelines were fitted against generated data and both returned valid delay probabilities/metrics.

Live Azure ML / MLflow tracking, model registry, and batch endpoint calls cannot be executed by the build environment because it has no access to your Azure subscription/credentials. Run the Azure validation commands in `README.md` from your machine; `python -m ml.verify_poc --tracking azure --check-registry` is the final machine-readable check.
