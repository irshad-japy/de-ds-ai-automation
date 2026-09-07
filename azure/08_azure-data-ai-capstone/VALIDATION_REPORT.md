# Validation report

Validation performed while packaging this POC:

- Python source compiled successfully with `python -m compileall`.
- `python -m scripts.verify_config --profile local` passed.
- `python -m scripts.smoke_test` passed.
- Local Bronze -> Silver -> Gold result: 10 orders, total revenue 675.50, average order value 67.55.
- `pytest -q` passed: 4 tests.
- Synthetic invoice PDF was generated and opens as a valid PDF file.

Not executed during packaging:

- Live Azure calls, because no user Azure credentials/subscription are available in the packaging environment.
- `terraform validate`, because Terraform CLI is not installed in the packaging environment. The Terraform resource shapes were cross-checked against current HashiCorp/AzureRM documentation, but you should still run the README validation commands before applying.
- Bicep deployment, because Azure CLI is not available in the packaging environment.

The README deliberately asks you to test each Azure integration separately before moving to the next one.
