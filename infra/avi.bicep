param location string
param storageAccountName string
param videoIndexerAccountName string

var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' 
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

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(storageAccount.id, videoIndexerAccountName, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: videoIndexer.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output videoIndexerAccountName string = videoIndexer.name
