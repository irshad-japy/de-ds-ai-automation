# Terraform mini-lab

The portal path in the root README is intentionally first because this POC is beginner-focused. Once you understand each service, use this folder to recreate the infrastructure.

## 1. Authenticate

```powershell
az login
az account show -o table
```

## 2. Create your local variables file

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with unique names and a strong bootstrap SQL password.

**Do not commit `terraform.tfvars`.** The repository `.gitignore` excludes it.

## 3. Initialize and validate

```powershell
terraform init
terraform fmt -recursive
terraform validate
terraform plan
```

Read the plan before applying.

## 4. Apply

```powershell
terraform apply
```

Type the Terraform confirmation only after you verify the plan is creating resources in `rg-azde-poc01-dev`.

## 5. Important post-deployment step: Azure SQL Entra admin

This Terraform mini-lab deliberately leaves Microsoft Entra SQL-server administration as an explicit learning step because the admin identity differs by tenant/account.

After deployment:

1. Azure Portal → your SQL logical server.
2. Set a Microsoft Entra admin you control.
3. Connect to the POC database as that Entra admin.
4. Run `sql/001_create_tables.sql`.
5. Run `sql/002_merge_orders.sql`.
6. Replace `<ADF_NAME>` and run `sql/003_create_adf_user.sql`.

## 6. Networking note

For the beginner version, the Terraform file creates the special SQL firewall rule `0.0.0.0` used by Azure SQL to allow Azure services. This is not the hardened enterprise design.

Hardened version:

- ADF Managed Virtual Network
- Managed private endpoint to Azure SQL
- Managed private endpoint to ADLS Gen2
- Private Endpoint / Private Link
- public network access disabled after private connectivity works

## 7. Cost note

The SQL database defaults to `Basic` for a small lab. Verify the actual price/availability in your Azure region before applying. Delete the Resource Group after the lab.

## 8. Destroy

Preferred cleanup for this isolated POC:

```powershell
terraform destroy
```

or delete the full Resource Group after checking its name.
