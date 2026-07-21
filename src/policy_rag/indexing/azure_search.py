"""Azure AI Search schema for canonical policy chunks."""

from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchField,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)

EMBEDDING_DIMENSIONS = 3072
AZURE_SEARCH_API_VERSION = "2025-09-01"
VECTOR_ALGORITHM_NAME = "policy-chunks-hnsw"
VECTOR_PROFILE_NAME = "policy-chunks-vector-profile"


def create_policy_chunk_search_index(name: str) -> SearchIndex:
    """Create the Azure AI Search index definition for policy chunks."""

    fields = [
        SimpleField(
            name="id",
            type="Edm.String",
            key=True,
            filterable=True,
        ),
        SimpleField(
            name="chunk_id",
            type="Edm.String",
            filterable=True,
        ),
        SearchField(
            name="text",
            type="Edm.String",
            searchable=True,
        ),
        SearchField(
            name="embedding",
            type="Collection(Edm.Single)",
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name=VECTOR_PROFILE_NAME,
        ),
        SimpleField(
            name="document_id",
            type="Edm.String",
            filterable=True,
        ),
        SearchField(
            name="document_title",
            type="Edm.String",
            searchable=True,
            filterable=True,
        ),
        SimpleField(
            name="version",
            type="Edm.String",
            filterable=True,
        ),
        SimpleField(
            name="effective_from",
            type="Edm.DateTimeOffset",
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="effective_to",
            type="Edm.DateTimeOffset",
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="department",
            type="Edm.String",
            filterable=True,
        ),
        SimpleField(
            name="classification",
            type="Edm.String",
            filterable=True,
        ),
        SearchField(
            name="allowed_groups",
            type="Collection(Edm.String)",
            filterable=True,
        ),
        SimpleField(
            name="section_id",
            type="Edm.String",
            filterable=True,
        ),
        SimpleField(
            name="section_number",
            type="Edm.String",
            filterable=True,
        ),
        SearchField(
            name="section_title",
            type="Edm.String",
            searchable=True,
        ),
        SimpleField(
            name="section_ordinal",
            type="Edm.Int32",
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="chunk_ordinal",
            type="Edm.Int32",
            filterable=True,
            sortable=True,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name=VECTOR_ALGORITHM_NAME,
                parameters=HnswParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE,
                ),
            )
        ],
        profiles=[
            VectorSearchProfile(
                name=VECTOR_PROFILE_NAME,
                algorithm_configuration_name=VECTOR_ALGORITHM_NAME,
            )
        ],
    )

    return SearchIndex(
        name=name,
        fields=fields,
        vector_search=vector_search,
    )
