# Delete the entire POC resource group when you are finished.
$RG = "rg-poc04-docintel"
Write-Host "This will permanently delete resource group: $RG" -ForegroundColor Yellow
$answer = Read-Host "Type DELETE to continue"
if ($answer -eq "DELETE") {
    az group delete --name $RG --yes --no-wait
    Write-Host "Deletion started."
} else {
    Write-Host "Cancelled."
}
