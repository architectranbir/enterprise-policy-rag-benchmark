"""Common retrieval interface shared by every vector backend."""

from typing import Protocol

from policy_rag.indexing import IndexedPolicyChunk
from policy_rag.retrieval.models import PolicyRetrievalRequest, RetrievedPolicyChunk


class PolicyVectorStore(Protocol):
    """Ingest and retrieve canonical policy chunks."""

    @property
    def backend_name(self) -> str: ...

    def initialize(self) -> None: ...

    def upsert(self, documents: tuple[IndexedPolicyChunk, ...]) -> None: ...

    def retrieve(self, request: PolicyRetrievalRequest) -> tuple[RetrievedPolicyChunk, ...]: ...

    def ready(self) -> bool: ...

    def close(self) -> None: ...
