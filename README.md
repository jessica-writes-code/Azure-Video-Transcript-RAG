# Azure Video Indexer Transcript RAG

This project is a work-in-progress effort to create a retrieval-augmented generation (RAG) large language model (LLM) system using transcripts from Azure Video Indexer.

## How To

1. Set up the Python environment, activate it, and install requirements from requirements.txt.

2. Deploy the infrastructure.

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

3. Deploy the transcript extraction function to Azure Function App.

```
cd functions/etl
func azure functionapp publish <AppConfigName>
```

4. Deploy the Azure AI Search components - data source, skill set, indexer.

a. Collect the information you'll need for deployment of Azure AI Search components.
    - SearchURL. This should be of the form https://<SearchResourceName>.search.windows.net.
    - SearchAPIKey. This should be a long alpha-numeric string, found under "Settings" -> "Keys".
    - OpenAIURL. This should be of the form https://<OpenAIResourceName>.openai.azure.com.
    - StorageConnectionString. This should be the connection string for the primary storage account, found under "Security + networking" -> "Access keys".

c. 
```
python srch/setup.py --srch-url "<SearchURL>" --srch-api-key "<SearchAPIKey>" --openai-url "<OpenAIURL>" --st-connection-string "<StorageConnectionString>"
```