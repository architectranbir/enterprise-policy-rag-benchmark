"""Provider-neutral embedding contracts and implementations."""

from policy_rag.embeddings.foundry import FoundryEmbeddingProvider
from policy_rag.embeddings.provider import EmbeddingProvider, EmbeddingVector

__all__ = [
    "EmbeddingProvider",
    "EmbeddingVector",
    "FoundryEmbeddingProvider",
]
