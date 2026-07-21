from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from policy_rag.domain.chunk import PolicyChunk
from policy_rag.domain.policy import PolicyClassification
from policy_rag.embeddings import EmbeddingProvider, EmbeddingVector
from policy_rag.ingestion.chunk_text import policy_chunk_text


class IndexedPolicyChunk(BaseModel):
    """Backend-neutral chunk document shared by every retrieval implementation."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    chunk_id: str
    text: str = Field(min_length=1)
    embedding: EmbeddingVector = Field(min_length=1)

    document_id: str
    document_title: str
    version: str
    effective_from: date
    effective_to: date | None
    department: str
    classification: PolicyClassification
    allowed_groups: tuple[str, ...]

    section_id: str
    section_number: str
    section_title: str
    section_ordinal: int = Field(ge=1)
    chunk_ordinal: int = Field(ge=1)


def policy_chunk_to_indexed_document(
    chunk: PolicyChunk,
    embedding: EmbeddingVector,
) -> IndexedPolicyChunk:
    """Combine one canonical chunk with its embedding for backend ingestion."""

    policy = chunk.section.policy

    return IndexedPolicyChunk(
        chunk_id=chunk.chunk_id,
        text=policy_chunk_text(chunk),
        embedding=embedding,
        document_id=policy.document_id,
        document_title=policy.title,
        version=policy.version,
        effective_from=policy.effective_from,
        effective_to=policy.effective_to,
        department=policy.department,
        classification=policy.classification,
        allowed_groups=policy.allowed_groups,
        section_id=chunk.section.section_id,
        section_number=chunk.section.section_number,
        section_title=chunk.section.title,
        section_ordinal=chunk.section.ordinal,
        chunk_ordinal=chunk.ordinal,
    )


def embed_policy_chunk(
    chunk: PolicyChunk,
    provider: EmbeddingProvider,
) -> IndexedPolicyChunk:
    """Embed and index the same canonical text for one policy chunk."""

    canonical_text = policy_chunk_text(chunk)
    embeddings = provider.embed((canonical_text,))

    if len(embeddings) != 1:
        raise ValueError(f"Expected one embedding for one policy chunk, received {len(embeddings)}")

    return policy_chunk_to_indexed_document(chunk, embeddings[0])
