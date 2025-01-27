param name string
param location string

resource search 'Microsoft.Search/searchServices@2020-08-01' = {
  name: name
  location: location
  sku: {
    name: 'standard'
  }
  properties: {
    replicaCount: 2
    partitionCount: 2
    hostingMode: 'default'
  }
  identity: {
    type: 'SystemAssigned'
  }
}
