@description('Azure region')
param location string = resourceGroup().location

@description('Globally unique lowercase storage account name')
param storageAccountName string

var commonTags = {
  project: 'azure-poc'
  environment: 'dev'
  owner: 'personal'
  autoDelete: 'true'
}

resource storage 'Microsoft.Storage/storageAccounts@2025-01-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  tags: commonTags
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2025-01-01' = {
  parent: storage
  name: 'default'
}

resource landing 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-01-01' = {
  parent: blobService
  name: 'landing'
  properties: {
    publicAccess: 'None'
  }
}

resource archive 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-01-01' = {
  parent: blobService
  name: 'archive'
  properties: {
    publicAccess: 'None'
  }
}

resource quarantine 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-01-01' = {
  parent: blobService
  name: 'quarantine'
  properties: {
    publicAccess: 'None'
  }
}

output storageId string = storage.id
output dfsEndpoint string = storage.properties.primaryEndpoints.dfs
