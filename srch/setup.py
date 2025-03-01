# Credit to https://github.com/Azure-Samples/azure-search-python-samples/blob/main/Tutorial-RAG/Tutorial-rag.ipynb
import argparse

from azure.core.credentials import AzureKeyCredential
from azure.identity import get_bearer_token_provider
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


def create_index(
    srch_url: str,
    srch_api_key: str,
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
    index_client = SearchIndexClient(srch_url, AzureKeyCredential(srch_api_key))
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


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--srch-url", type=str, required=True)
    parser.add_argument("--srch-api-key", type=str, required=True)
    parser.add_argument("--openai-url", type=str, required=True)

    args = parser.parse_args()

    # Execute setup
    create_index(args.srch_url, args.srch_api_key, args.openai_url)
