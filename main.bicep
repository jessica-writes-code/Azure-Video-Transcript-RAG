targetScope='subscription'

param location string
param resourceGroupName string

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
}

// Deploy video indexer resources, including associated storage account
module videoIndexer 'videoindexer.bicep' = {
  name: 'videoIndexerModule'
  scope: resourceGroup
  params: {
    location: location
    storageAccountName: 'st${uniqueString(resourceGroup.id)}avi'
    videoIndexerAccountName: 'avi-${uniqueString(resourceGroup.id)}'
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
      resourceGroup.name
      videoIndexer.outputs.videoIndexerAccountName
      subscription().subscriptionId
      storageAcct.outputs.blobContainerUrl
      'full-transcripts'
    ]
  }
}

module roleAssignment 'roleassignment.bicep' = {
  name: 'grant-storage-blob-data-contributor'
  scope: resourceGroup
  params: {
    servicePrincipalObjectId: videoIndexer.outputs.servicePrincipalId
    storageAccountName: videoIndexer.outputs.storageAccountName
  }
}
