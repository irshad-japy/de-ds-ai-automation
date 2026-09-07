@echo off
setlocal
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%\terraform"

echo === Terraform state resources ===
terraform state list

echo.
echo === Outputs ===
terraform output

echo.
for /f "usebackq delims=" %%A in (`terraform output -raw resource_group_name`) do set "RG=%%A"
if not "%RG%"=="" (
  echo.
  echo === Azure resources in %RG% ===
  az resource list --resource-group "%RG%" --query "[].{Name:name,Type:type,Location:location}" --output table
)
endlocal
