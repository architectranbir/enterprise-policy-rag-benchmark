"""Azure AI Search implementation of the common vector-store contract."""

from typing import Protocol

from policy_rag.indexing import IndexedPolicyChunk
from policy_rag.indexing.azure_ingestion import (
    AzureSearchUploadClient,
    upload_indexed_policy_chunks,
)
from policy_rag.retrieval.azure_retrieval import (
    AzureSearchQueryClient,
    retrieve_optimized_policy_chunks,
    retrieve_vector_policy_chunks,
)
from policy_rag.retrieval.models import PolicyRetrievalRequest, RetrievalMode, RetrievedPolicyChunk


class AzureSearchClient(AzureSearchQueryClient, AzureSearchUploadClient, Protocol):
    def get_document_count(self) -> int: ...

    def close(self) -> None: ...


class AzureAISearchStore:
    def __init__(self, client: AzureSearchClient) -> None:
        self._client = client

    @property
    def backend_name(self) -> str:
        return "azure_ai_search"

    def initialize(self) -> None:
        """The Azure index is managed separately by the index deployment step."""

    def upsert(self, documents: tuple[IndexedPolicyChunk, ...]) -> None:
        upload_indexed_policy_chunks(self._client, documents)

    def retrieve(self, request: PolicyRetrievalRequest) -> tuple[RetrievedPolicyChunk, ...]:
        if request.mode is RetrievalMode.PLATFORM_OPTIMIZED:
            return retrieve_optimized_policy_chunks(self._client, request)
        return retrieve_vector_policy_chunks(self._client, request)

    def ready(self) -> bool:
        try:
            self._client.get_document_count()
            return True
        except Exception:
            return False

    def close(self) -> None:
        self._client.close()
