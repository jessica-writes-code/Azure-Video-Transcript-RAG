param storageLocation string
param storageName string

// Create a storage account & associated containers for transcripts
resource storageAcct 'Microsoft.Storage/storageAccounts@2023-04-01' = {
  name: storageName
  location: storageLocation
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'Storage'
  properties: {}
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-04-01' = {
  parent: storageAcct
  name: 'default'
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-04-01' = {
  parent: blobService
  name: 'full-transcripts'
  properties: {}
}

output blobContainerUrl string = concat(storageAcct.properties.primaryEndpoints.blob)
