from pydantic import BaseModel, ConfigDict, Field

from policy_rag.domain.policy import PolicyDocument


class PolicySection(BaseModel):
    """One logical section extracted from a policy document."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    section_id: str = Field(
        min_length=5,
        max_length=200,
        pattern=r"^[A-Z0-9_.:-]+$",
    )
    policy: PolicyDocument
    section_number: str = Field(
        min_length=1,
        max_length=30,
        pattern=r"^\d+(?:\.\d+)*$",
    )
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    ordinal: int = Field(ge=1)
    heading_level: int = Field(ge=2, le=6)
