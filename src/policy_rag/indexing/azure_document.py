"""Map backend-neutral policy chunks to Azure AI Search documents."""

from base64 import urlsafe_b64encode
from datetime import UTC, date, datetime, time
from typing import TypedDict

from policy_rag.indexing.azure_search import EMBEDDING_DIMENSIONS
from policy_rag.indexing.document import IndexedPolicyChunk


class AzurePolicyChunkDocument(TypedDict):
    """Document payload matching the Azure AI Search policy-chunk schema."""

    id: str
    chunk_id: str
    text: str
    embedding: list[float]
    document_id: str
    document_title: str
    version: str
    effective_from: datetime
    effective_to: datetime | None
    department: str
    classification: str
    allowed_groups: list[str]
    section_id: str
    section_number: str
    section_title: str
    section_ordinal: int
    chunk_ordinal: int


def azure_document_key(chunk_id: str) -> str:
    """Encode a canonical chunk ID as an Azure-safe document key."""

    return urlsafe_b64encode(chunk_id.encode()).decode()


def date_at_utc_midnight(value: date | None) -> datetime | None:
    """Convert a policy date to an Azure DateTimeOffset-compatible value."""

    if value is None:
        return None

    return datetime.combine(value, time.min, tzinfo=UTC)


def indexed_chunk_to_azure_document(
    document: IndexedPolicyChunk,
) -> AzurePolicyChunkDocument:
    """Create an Azure upload payload without changing canonical data."""

    if len(document.embedding) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSIONS} embedding dimensions, "
            f"received {len(document.embedding)}"
        )

    effective_from = date_at_utc_midnight(document.effective_from)
    if effective_from is None:
        raise ValueError("effective_from must not be None")

    return AzurePolicyChunkDocument(
        id=azure_document_key(document.chunk_id),
        chunk_id=document.chunk_id,
        text=document.text,
        embedding=list(document.embedding),
        document_id=document.document_id,
        document_title=document.document_title,
        version=document.version,
        effective_from=effective_from,
        effective_to=date_at_utc_midnight(document.effective_to),
        department=document.department,
        classification=document.classification.value,
        allowed_groups=list(document.allowed_groups),
        section_id=document.section_id,
        section_number=document.section_number,
        section_title=document.section_title,
        section_ordinal=document.section_ordinal,
        chunk_ordinal=document.chunk_ordinal,
    )
