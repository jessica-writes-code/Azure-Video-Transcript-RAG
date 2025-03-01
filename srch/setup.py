# Credit to https://github.com/Azure-Samples/azure-search-python-samples/blob/main/Tutorial-RAG/Tutorial-rag.ipynb
import argparse

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    AzureOpenAIEmbeddingSkill,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    CognitiveServicesAccountKey,
    HnswAlgorithmConfiguration,
    IndexProjectionMode,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    SearchIndexerSkillset,
    SplitSkill,
    VectorSearch,
    VectorSearchProfile,
)


INDEX_NAME = "rag-transcript-index"
DATA_SOURCE_NAME = "rag-transcript-ds"
SKILLSET_NAME = "rag-transcript-ss"
INDEXER_NAME = "rag-transcript-idxr"


def create_index(
    index_client: SearchIndexClient,
    openai_url: str,
) -> None:
    """
    Creates an Azure Search index for RAG.

    Args:
        index_client (SearchIndexClient): Azure Search index client.
        openai_url (str): Azure OpenAI resource URL.
    Returns:
        None
    """

    # Create a search index
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
    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
    index_client.create_or_update_index(index)


def create_datasource(
    indexer_client: SearchIndexerClient, st_connection_string: str
) -> None:
    """
    Creates an Azure Search data source for RAG.

    Args:
        indexer_client (SearchIndexerClient): Azure Search indexer client.
        st_connection_string (str): Azure Storage connection string.
    Returns:
        None
    """
    container = SearchIndexerDataContainer(name="full-transcripts")
    data_source_connection = SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type="azureblob",
        connection_string=st_connection_string,
        container=container,
    )
    indexer_client.create_or_update_data_source_connection(data_source_connection)


def create_skillset(
    indexer_client: SearchIndexerClient,
    openai_url: str,
    cognitive_services_account: CognitiveServicesAccountKey,
) -> None:
    """
    Creates an Azure Search skillset for RAG.

    Args:
        indexer_client (SearchIndexerClient): Azure Search indexer client.
        openai_url (str): Azure OpenAI resource URL.
        cognitive_services_account (CognitiveServicesAccountKey): Cognitive services account key.
    Returns:
        None
    """

    split_skill = SplitSkill(
        description="Split skill to chunk documents",
        text_split_mode="pages",
        context="/document",
        maximum_page_length=2000,
        page_overlap_length=500,
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/content"),
        ],
        outputs=[OutputFieldMappingEntry(name="textItems", target_name="pages")],
    )

    embedding_skill = AzureOpenAIEmbeddingSkill(
        description="Skill to generate embeddings via Azure OpenAI",
        context="/document/pages/*",
        resource_url=openai_url,
        deployment_name="text-embedding-3-large",
        model_name="text-embedding-3-large",
        dimensions=1024,
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/pages/*"),
        ],
        outputs=[OutputFieldMappingEntry(name="embedding", target_name="text_vector")],
    )

    index_projections = SearchIndexerIndexProjection(
        selectors=[
            SearchIndexerIndexProjectionSelector(
                target_index_name=INDEX_NAME,
                parent_key_field_name="parent_id",
                source_context="/document/pages/*",
                mappings=[
                    InputFieldMappingEntry(name="chunk", source="/document/pages/*"),
                    InputFieldMappingEntry(
                        name="text_vector", source="/document/pages/*/text_vector"
                    ),
                    InputFieldMappingEntry(
                        name="title", source="/document/metadata_storage_name"
                    ),
                ],
            ),
        ],
        parameters=SearchIndexerIndexProjectionsParameters(
            projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
        ),
    )

    skills = [split_skill, embedding_skill]
    skillset = SearchIndexerSkillset(
        name=SKILLSET_NAME,
        description="Skillset to chunk documents and generating embeddings",
        skills=skills,
        index_projection=index_projections,
        cognitive_services_account=cognitive_services_account,
    )

    indexer_client.create_or_update_skillset(skillset)
    print(f"{skillset.name} created")


def create_indexer(
    indexer_client: SearchIndexerClient,
    index_name: str,
    data_source_name: str,
    skillset_name: str,
) -> None:
    """
    Creates an Azure Search indexer for RAG.

    Args:
        indexer_client (SearchIndexerClient): Azure Search indexer client.
        index_name (str): Azure Search index name.
        data_source_name (str): Azure Search data source name.
        skillset_name (str): Azure Search skillset name.
    Returns:
        None
    """

    indexer_parameters = None
    indexer = SearchIndexer(
        name=INDEXER_NAME,
        description="Indexer to index documents and generate embeddings",
        skillset_name=skillset_name,
        target_index_name=index_name,
        data_source_name=data_source_name,
        parameters=indexer_parameters,
    )

    indexer_client.create_or_update_indexer(indexer)
    print(
        f"{INDEXER_NAME} is created and running. Give the indexer a few minutes before running a query."
    )


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--srch-url", type=str, required=True)
    parser.add_argument("--srch-api-key", type=str, required=True)
    parser.add_argument("--openai-url", type=str, required=True)
    parser.add_argument("--st-connection-string", type=str, required=True)
    parser.add_argument("--ai-multiservice-account-key", type=str, required=True)

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
    create_datasource(indexer_client, args.st_connection_string)

    # - Create skillset
    cognitive_services_account = CognitiveServicesAccountKey(
        key=args.ai_multiservice_account_key
    )
    create_skillset(indexer_client, args.openai_url, cognitive_services_account)

    # - Create indexer
    create_indexer(indexer_client, INDEX_NAME, DATA_SOURCE_NAME, SKILLSET_NAME)
