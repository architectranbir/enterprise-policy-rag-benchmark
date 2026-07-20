from typing import cast

from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    VectorSearchAlgorithmMetric,
)

from policy_rag.indexing.azure_search import (
    EMBEDDING_DIMENSIONS,
    VECTOR_ALGORITHM_NAME,
    VECTOR_PROFILE_NAME,
    create_policy_chunk_search_index,
)


def fields_by_name(index_name: str) -> dict[str, SearchField]:
    index = create_policy_chunk_search_index(index_name)
    return {field.name: field for field in index.fields}


def test_schema_defines_key_text_and_vector_fields() -> None:
    index = create_policy_chunk_search_index("policy-chunks")
    fields = fields_by_name(index.name)

    assert index.name == "policy-chunks"
    assert fields["id"].key is True
    assert fields["chunk_id"].filterable is True
    assert fields["text"].searchable is True

    embedding = fields["embedding"]
    assert embedding.type == "Collection(Edm.Single)"
    assert embedding.searchable is True
    assert embedding.vector_search_dimensions == EMBEDDING_DIMENSIONS
    assert embedding.vector_search_profile_name == VECTOR_PROFILE_NAME


def test_schema_supports_acl_policy_and_citation_filters() -> None:
    fields = fields_by_name("policy-chunks")

    filterable_fields = {
        "document_id",
        "version",
        "effective_from",
        "effective_to",
        "department",
        "classification",
        "allowed_groups",
        "section_id",
        "section_number",
        "section_ordinal",
        "chunk_ordinal",
    }

    assert all(fields[name].filterable is True for name in filterable_fields)
    assert fields["effective_from"].sortable is True
    assert fields["effective_to"].sortable is True


def test_schema_uses_cosine_hnsw_vector_search() -> None:
    index = create_policy_chunk_search_index("policy-chunks")

    assert index.vector_search is not None
    assert index.vector_search.algorithms is not None
    assert index.vector_search.profiles is not None

    algorithm = cast(
        HnswAlgorithmConfiguration,
        index.vector_search.algorithms[0],
    )
    profile = index.vector_search.profiles[0]

    assert algorithm.name == VECTOR_ALGORITHM_NAME
    assert algorithm.parameters is not None
    assert algorithm.parameters.metric == VectorSearchAlgorithmMetric.COSINE
    assert profile.name == VECTOR_PROFILE_NAME
    assert profile.algorithm_configuration_name == VECTOR_ALGORITHM_NAME
