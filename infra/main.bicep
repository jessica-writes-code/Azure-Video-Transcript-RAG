targetScope='subscription'

param location string
param resourceGroupName string
param existingAVIName string = '' // Set to empty string for new deployment or provide existing AVI resource ID
param existingAVIResourceGroupName string = '' // Set to empty string for new deployment or provide existing resource group name

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
}

// Deploy video indexer resources, including associated storage account
// TODO: Combine the provisioning & role assignment modules into a single module.
module videoIndexer 'avi.bicep' = if (existingAVIName == '') {
  name: 'create-video-indexer'
  scope: resourceGroup
  params: {
    location: location
    storageAccountName: 'st${uniqueString(resourceGroup.id)}avi'
    videoIndexerAccountName: 'avi-${uniqueString(resourceGroup.id)}'
  }
}

// Deploy independent storage resources
module storageAcct 'storage.bicep' = {
  name: 'create-storage'
  scope: resourceGroup
  params: {
    storageLocation: location
    storageName: 'st${uniqueString(resourceGroup.id)}'
  }
}

// Deploy app configuration resources
module appConfiguration 'appconfiguration.bicep' = {
  name: 'create-app-configuration'
  scope: resourceGroup
  params: {
    configStoreName: 'appconfig${uniqueString(resourceGroup.id)}'
    location: location
    keyValueNames: [
      'AVIResourceGroup'
      'AVIResourceName'
      'AVISubscriptionID'
      'TranscriptsStorageURL'
      'TranscriptsStorageContainerName'
    ]
    keyValueValues: [
      ((existingAVIName == '') ? resourceGroup.name : existingAVIResourceGroupName)
      ((existingAVIName == '') ? videoIndexer.outputs.videoIndexerAccountName : existingAVIName)
      subscription().subscriptionId
      storageAcct.outputs.blobContainerUrl
      'full-transcripts'
    ]
  }
}

// Deploy function app resources
module functionApp 'functionapp.bicep' = {
  name: 'create-function-app'
  scope: resourceGroup
  params: {
    appConfigurationEndpoint: appConfiguration.outputs.configEndpoint
    location: resourceGroup.location
  }
}

// - Grant all roles, except those related to video indexer -
// TODO: Break up the two role assignments into separate modules.
module functionAppRoleAssignment 'functionapproleassignment.bicep' = {
  name: 'grant-roles-to-function-app'
  scope: resourceGroup
  params: {
    servicePrincipalObjectId: functionApp.outputs.functionAppPrincipalId
    appConfigurationAccountName: appConfiguration.outputs.configName
    storageAccountName: storageAcct.outputs.storageAccountName
  }
}

// - Grant roles related to video indexer, if the video indexer is new -
// TODO: Combine the new/existing role assignment modules into a single module.
module functionAppVIRoleAssignment 'functionappviroleassignment.bicep' = if (existingAVIName == '') {
  name: 'grant-roles-to-function-app-for-new-video-indexer-access'
  scope: resourceGroup
  params: {
    servicePrincipalObjectId: functionApp.outputs.functionAppPrincipalId
    videoIndexerName: videoIndexer.outputs.videoIndexerAccountName
  }
}

// - Grant roles related to video indexer, if the video indexer is existing -
resource existingAVIResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' existing = {
  name: existingAVIResourceGroupName
}

module functionAppExistingVIRoleAssignment 'functionappviroleassignment.bicep' = if (existingAVIName != '') {
  name: 'grant-existing-video-indexer-roles'
  scope: existingAVIResourceGroup
  params: {
    servicePrincipalObjectId: functionApp.outputs.functionAppPrincipalId
    videoIndexerName: existingAVIName
  }
}

// Deploy OpenAI resources
module openAI 'oai.bicep' = {
  name: 'create-openai-resources'
  scope: resourceGroup
  params: {
    location: location
    openAIAccountName: 'oai-${uniqueString(resourceGroup.id)}'
  }
}

// Deploy search resources
module search 'srch.bicep' = {
  name: 'create-search-service'
  scope: resourceGroup
  params: {
    name: 'srch${uniqueString(resourceGroup.id)}'
    location: location
  }
}

module searchRoleAssignment 'st-reader-role-assignment.bicep' = {
  name: 'grant-storage-read-access-to-search-service'
  scope: resourceGroup
  params: {
    servicePrincipalId: search.outputs.servicePrincipalId
    storageAccountName: storageAcct.outputs.storageAccountName
  }
}

module oaiRoleAssignment 'oai-user-role-assignment.bicep' = {
  name: 'grant-openai-user-role-to-search-service'
  scope: resourceGroup
  params: {
    servicePrincipalId: search.outputs.servicePrincipalId
    oaiAccountName: openAI.outputs.openAIAccountName
  }
}
