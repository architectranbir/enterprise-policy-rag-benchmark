"""Backend-neutral indexing contracts."""

from policy_rag.indexing.document import (
    IndexedPolicyChunk,
    embed_policy_chunk,
    policy_chunk_to_indexed_document,
)

__all__ = [
    "IndexedPolicyChunk",
    "embed_policy_chunk",
    "policy_chunk_to_indexed_document",
]
