from pydantic import BaseModel, ConfigDict, Field

from policy_rag.domain.section import PolicySection


class PolicyChunk(BaseModel):
    """One retrievable text chunk from a policy section."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    chunk_id: str = Field(
        min_length=5,
        max_length=220,
        pattern=r"^[A-Z0-9_.:-]+$",
    )
    section: PolicySection
    content: str = Field(min_length=1)
    ordinal: int = Field(ge=1)
