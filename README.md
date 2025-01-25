# Azure Video Indexer Transcript RAG

This project is a work-in-progress effort to create a retrieval-augmented generation (RAG) large language model (LLM) system using transcripts from Azure Video Indexer.

## How To

Deploy the infrastructure.

```
az deployment sub create
--name <DeploymentName>
--location <DeploymentLocation>
--template-file infra/main.bicep
--parameters
resourceGroupName=<DeploymentResourceGroup>
location=<DeploymentLocation>
existingAVIName=<ExistingAzureVideoIndexer> (Optional)
existingAVIResourceGroupName=<ExistingAzureVideoIndexerRG> (Optional)
```

Deploy the function.

```
func azure functionapp publish <AppConfigName>
```

