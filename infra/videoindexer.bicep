param location string
param storageAccountName string
param videoIndexerAccountName string

var storageKind = 'StorageV2' 
var storageSku = 'Standard_LRS'

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  name: storageAccountName
  location: location
  kind: storageKind
  properties: {
    minimumTlsVersion: 'TLS1_2'
  }
  sku: {
    name: storageSku
  }
}

resource videoIndexer 'Microsoft.VideoIndexer/accounts@2024-01-01' = {
  name: videoIndexerAccountName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    storageServices: {
      resourceId: storageAccount.id
    }
  }
}

output storageAccountName string = storageAccount.name 
output videoIndexerAccountName string = videoIndexer.name
output servicePrincipalId string = videoIndexer.identity.principalId
