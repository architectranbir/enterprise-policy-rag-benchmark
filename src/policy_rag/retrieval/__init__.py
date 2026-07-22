"""Backend-neutral policy retrieval contracts."""

from policy_rag.retrieval.azure_retrieval import retrieve_vector_policy_chunks
from policy_rag.retrieval.models import (
    PolicyRetrievalRequest,
    RetrievedPolicyChunk,
)

__all__ = [
    "PolicyRetrievalRequest",
    "RetrievedPolicyChunk",
    "retrieve_vector_policy_chunks",
]
