"""Backend-neutral indexing contracts."""

from policy_rag.indexing.document import (
    IndexedPolicyChunk,
    policy_chunk_to_indexed_document,
)

__all__ = [
    "IndexedPolicyChunk",
    "policy_chunk_to_indexed_document",
]
