param(
    [Parameter(Mandatory=$true)][string]$ResourceGroup,
    [Parameter(Mandatory=$true)][string]$StorageAccount,
    [Parameter(Mandatory=$true)][string]$DataFactory,
    [Parameter(Mandatory=$true)][string]$SqlServer
)

$ErrorActionPreference = "Stop"

Write-Host "Checking active Azure account..."
az account show -o table

Write-Host "`nResource Group:"
az group show -n $ResourceGroup --query "{name:name,location:location,tags:tags}" -o jsonc

Write-Host "`nStorage Account:"
az storage account show -g $ResourceGroup -n $StorageAccount --query "{name:name,hns:isHnsEnabled,https:enableHttpsTrafficOnly,publicNetwork:publicNetworkAccess,tags:tags}" -o jsonc

Write-Host "`nData Factory:"
az datafactory show -g $ResourceGroup -n $DataFactory --query "{name:name,location:location,identity:identity}" -o jsonc

Write-Host "`nSQL logical server:"
az sql server show -g $ResourceGroup -n $SqlServer --query "{name:name,fqdn:fullyQualifiedDomainName,publicNetwork:publicNetworkAccess,minTls:minimalTlsVersion,tags:tags}" -o jsonc

Write-Host "`nResources in POC Resource Group:"
az resource list -g $ResourceGroup --query "[].{name:name,type:type,location:location}" -o table
