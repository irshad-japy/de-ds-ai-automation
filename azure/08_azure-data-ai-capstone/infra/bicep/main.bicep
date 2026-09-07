targetScope = 'resourceGroup'

param location string = resourceGroup().location
param storageName string
param logAnalyticsName string

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
  }
}

resource logs 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    retentionInDays: 30
  }
  sku: { name: 'PerGB2018' }
}

output storageDfsEndpoint string = storage.properties.primaryEndpoints.dfs
