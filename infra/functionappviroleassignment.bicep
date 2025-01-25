param servicePrincipalObjectId string
param videoIndexerName string

resource videoIndexer 'Microsoft.CognitiveServices/accounts@2021-04-30' existing = {
  name: videoIndexerName
}

resource videoIndexerReaderRole 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(videoIndexer.id, servicePrincipalObjectId, 'Contributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c')
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}
