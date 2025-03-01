# Credit to https://github.com/Azure-Samples/azure-search-python-samples/blob/main/Tutorial-RAG/Tutorial-rag.ipynb
import argparse

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SearchIndex,
)
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
)


def create_index(
    index_client: SearchIndexClient,
    openai_url: str,
) -> None:
    """
    Creates an Azure Search index for RAG.

    Args:
        srch_url (str): Azure Search service URL.
        srch_api_key (str): Azure Search service API key.
        openai_url (str): OpenAI service URL.
    Returns:
        None
    """

    # Create a search index
    index_name = "rag-transcript-index"
    fields = [
        SearchField(name="parent_id", type=SearchFieldDataType.String),
        SearchField(name="title", type=SearchFieldDataType.String),
        SearchField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            key=True,
            sortable=True,
            filterable=True,
            facetable=True,
            analyzer_name="keyword",
        ),
        SearchField(
            name="chunk",
            type=SearchFieldDataType.String,
            sortable=False,
            filterable=False,
            facetable=False,
        ),
        SearchField(
            name="text_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1024,
            vector_search_profile_name="myHnswProfile",
        ),
    ]

    # Configure the vector search configuration
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="myHnsw"),
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
                vectorizer_name="myOpenAI",
            )
        ],
        vectorizers=[
            AzureOpenAIVectorizer(
                vectorizer_name="myOpenAI",
                kind="azureOpenAI",
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=openai_url,
                    deployment_name="text-embedding-3-large",
                    model_name="text-embedding-3-large",
                ),
            ),
        ],
    )

    # Create the search index
    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
    index_client.create_or_update_index(index)


def create_datasource(
    indexer_client: SearchIndexerClient, st_connection_string: str
) -> None:
    """
    TODO
    """

    # Create a data source
    container = SearchIndexerDataContainer(name="full-transcripts")
    data_source_connection = SearchIndexerDataSourceConnection(
        name="rag-transcript-ds",
        type="azureblob",
        connection_string=st_connection_string,
        container=container,
    )
    data_source = indexer_client.create_or_update_data_source_connection(
        data_source_connection
    )

    print(f"Data source '{data_source.name}' created or updated")


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--srch-url", type=str, required=True)
    parser.add_argument("--srch-api-key", type=str, required=True)
    parser.add_argument("--openai-url", type=str, required=True)
    parser.add_argument("--st-connection-string", type=str, required=True)

    args = parser.parse_args()

    # Execute setup
    # - Create index
    index_client = SearchIndexClient(
        args.srch_url, AzureKeyCredential(args.srch_api_key)
    )
    create_index(index_client, args.openai_url)

    # - Create data source
    indexer_client = SearchIndexerClient(
        args.srch_url, AzureKeyCredential(args.srch_api_key)
    )
    print(args.st_connection_string)
    create_datasource(indexer_client, args.st_connection_string)
