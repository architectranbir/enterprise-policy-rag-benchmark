from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PolicyAccessContext(BaseModel):
    """Identity and date context used when retrieving policies."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    user_id: str = Field(min_length=1, max_length=200)
    user_groups: tuple[str, ...]
    as_of: date
