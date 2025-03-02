// This Bicep file creates a role assignment for a service to use a search service.
param servicePrincipalId string
param oaiAccountName string

resource oaiAccount 'Microsoft.Storage/storageAccounts@2021-04-01' existing = {
  name: oaiAccountName
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(oaiAccount.id, servicePrincipalId, 'Cognitive Services OpenAI User')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
    principalId: servicePrincipalId
    principalType: 'ServicePrincipal'
  }
}
