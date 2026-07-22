"""Select exactly one retrieval backend from configuration."""

from collections.abc import Mapping
from enum import StrEnum

from policy_rag.retrieval.base import PolicyVectorStore


class VectorBackend(StrEnum):
    AZURE_AI_SEARCH = "azure_ai_search"
    PGVECTOR = "pgvector"
    QDRANT = "qdrant"


def create_vector_store(
    backend: VectorBackend, stores: Mapping[VectorBackend, PolicyVectorStore]
) -> PolicyVectorStore:
    try:
        return stores[backend]
    except KeyError as error:
        raise ValueError(f"Retrieval backend is not configured: {backend.value}") from error
