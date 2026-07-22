"""Backend-neutral policy retrieval contracts."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification


class PolicyRetrievalRequest(BaseModel):
    """Exact metadata filters plus the caller's access context."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    access: PolicyAccessContext
    document_id: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        pattern=r"^[A-Z0-9][A-Z0-9_-]*$",
    )
    department: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    classification: PolicyClassification | None = None
    query_embedding: tuple[float, ...] | None = Field(
        default=None,
        min_length=1,
    )
    limit: int = Field(default=10, ge=1, le=100)


class RetrievedPolicyChunk(BaseModel):
    """One backend-neutral policy chunk returned by retrieval."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    chunk_id: str
    text: str = Field(min_length=1)

    document_id: str
    document_title: str
    version: str
    effective_from: date
    effective_to: date | None
    department: str
    classification: PolicyClassification

    section_id: str
    section_number: str
    section_title: str
    section_ordinal: int = Field(ge=1)
    chunk_ordinal: int = Field(ge=1)

    score: float | None = None
