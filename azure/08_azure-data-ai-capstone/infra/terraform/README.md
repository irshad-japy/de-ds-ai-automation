# Terraform deployment

This Terraform intentionally deploys only a minimal reusable core by default: resource group, ADLS Gen2, Log Analytics, Application Insights, Key Vault, Event Hubs and Azure AI Search. Databricks is disabled by default because you should normally reuse the POC-02 workspace.

```powershell
cd infra\terraform
copy terraform.tfvars.example terraform.tfvars
# edit subscription_id and options
terraform fmt -recursive
terraform init
terraform validate
terraform plan -out poc08.tfplan
terraform apply poc08.tfplan
terraform output
```

Cleanup:

```powershell
terraform destroy
```

If `search_sku = "free"` fails because your subscription already has a free Search service, reuse that service or change the variable to an allowed paid SKU for a short lab and delete it after testing.
