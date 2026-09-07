param(
    [Parameter(Mandatory=$true)][string]$ResourceGroup,
    [switch]$ConfirmDelete
)

$ErrorActionPreference = "Stop"

if (-not $ConfirmDelete) {
    throw "Refusing to delete. Re-run with -ConfirmDelete after checking the Resource Group name."
}

Write-Host "About to delete Resource Group: $ResourceGroup"
az group show -n $ResourceGroup -o table

if ($ResourceGroup -ne "rg-azde-poc01-dev") {
    Write-Warning "The Resource Group name is not the default POC name. Double-check before continuing."
}

az group delete -n $ResourceGroup --yes
Write-Host "Delete request submitted for $ResourceGroup."
