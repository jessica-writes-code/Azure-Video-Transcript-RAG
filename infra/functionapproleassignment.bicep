param functionAppName string
param storageAccountName string
param videoIndexerAccountName string


resource storageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' existing = {
  name: storageAccountName
}

resource videoIndexer 'Microsoft.CognitiveServices/accounts@2021-04-30' existing = {
  name: videoIndexerAccountName
}

resource functionAppIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' existing = {
  name: '${functionAppName}-identity'
}

resource storageBlobContributorRole 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(storageAccount.id, functionAppIdentity.id, 'Storage Blob Data Contributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: functionAppIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource videoIndexerReaderRole 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(videoIndexer.id, functionAppIdentity.id, 'Video Indexer Restricted Viewer')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a2c4a527-7dc0-4ee3-897b-403ade70fafb')
    principalId: functionAppIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
