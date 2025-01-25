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
module videoIndexer 'videoindexer.bicep' = if (existingAVIName == '') {
  name: 'videoIndexerModule'
  scope: resourceGroup
  params: {
    location: location
    storageAccountName: 'st${uniqueString(resourceGroup.id)}avi'
    videoIndexerAccountName: 'avi-${uniqueString(resourceGroup.id)}'
  }
}

module videoIndexerRoleAssignment 'videoindexerroleassignment.bicep' = if (existingAVIName == '') {
  name: 'grant-storage-blob-data-contributor'
  scope: resourceGroup
  params: {
    servicePrincipalObjectId: videoIndexer.outputs.servicePrincipalId
    storageAccountName: videoIndexer.outputs.storageAccountName
  }
}

// Deploy independent storage resources
module storageAcct 'storage.bicep' = {
  name: 'storageModule'
  scope: resourceGroup
  params: {
    storageLocation: location
    storageName: 'st${uniqueString(resourceGroup.id)}'
  }
}

// Deploy app configuration resources
module appConfiguration 'appconfiguration.bicep' = {
  name: 'appConfigModule'
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
  name: 'functionAppModule'
  scope: resourceGroup
  params: {
    appConfigurationEndpoint: appConfiguration.outputs.configEndpoint
    location: resourceGroup.location
  }
}

module functionAppRoleAssignment 'functionapproleassignment.bicep' = {
  name: 'grant-function-app-accesses'
  scope: resourceGroup
  params: {
    servicePrincipalObjectId: functionApp.outputs.functionAppPrincipalId
    appConfigurationAccountName: appConfiguration.outputs.configName
    storageAccountName: storageAcct.outputs.storageAccountName
    videoIndexerAccountName: ((existingAVIName == '') ? videoIndexer.outputs.videoIndexerAccountName : existingAVIName)
  }
}
