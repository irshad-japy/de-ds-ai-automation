# Git / YAML CI concepts

The included `.github/workflows/ci.yml` demonstrates a safe CI gate that does not require Azure credentials. It installs dependencies, generates deterministic data, runs a local MLflow experiment, scores data, verifies the POC, and runs tests.

For a real release pipeline, separate stages should typically be:
1. code quality/unit tests;
2. reproducible training;
3. metric quality gate;
4. model registration;
5. approval;
6. batch/online deployment;
7. smoke test;
8. monitoring and rollback.

Do not put Azure secrets into YAML. Prefer workload identity/federated credentials for production CI.
