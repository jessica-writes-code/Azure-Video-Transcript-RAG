param appConfigurationAccountName string
param servicePrincipalObjectId string
param storageAccountName string
param videoIndexerAccountName string

resource appConfiguration 'Microsoft.AppConfiguration/configurationStores@2024-05-01' existing = {
  name: appConfigurationAccountName
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' existing = {
  name: storageAccountName
}

resource videoIndexer 'Microsoft.CognitiveServices/accounts@2021-04-30' existing = {
  name: videoIndexerAccountName
}

resource appConfigurationReaderRole 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(appConfiguration.id, servicePrincipalObjectId, 'App Configuration Data Reader')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '516239f1-63e1-4d78-a4de-a74fb236a071')
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

resource storageBlobContributorRole 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(storageAccount.id, servicePrincipalObjectId, 'Storage Blob Data Contributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

resource videoIndexerReaderRole 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(videoIndexer.id, servicePrincipalObjectId, 'Video Indexer Restricted Viewer')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a2c4a527-7dc0-4ee3-897b-403ade70fafb')
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}
