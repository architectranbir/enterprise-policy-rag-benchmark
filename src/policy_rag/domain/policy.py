from collections.abc import Collection
from datetime import date
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PolicyClassification(StrEnum):
    """Supported policy security classifications."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class PolicyDocument(BaseModel):
    """Validated metadata for one version of an enterprise policy."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    document_id: str = Field(
        min_length=3,
        max_length=100,
        pattern=r"^[A-Z0-9][A-Z0-9_-]*$",
    )
    title: str = Field(min_length=1, max_length=200)
    version: str = Field(min_length=1, max_length=50)
    effective_from: date
    effective_to: date | None = None
    department: str = Field(min_length=1, max_length=100)
    classification: PolicyClassification
    allowed_groups: tuple[str, ...] = Field(min_length=1)

    def is_effective_on(self, as_of: date) -> bool:
        """Return whether this policy version is effective on a given date."""
        starts_on_or_before = self.effective_from <= as_of
        has_not_ended = self.effective_to is None or as_of <= self.effective_to

        return starts_on_or_before and has_not_ended

    def is_accessible_to(self, user_groups: Collection[str]) -> bool:
        """Return whether the user belongs to an allowed policy group."""
        allowed_groups = frozenset(self.allowed_groups)

        return not allowed_groups.isdisjoint(user_groups)

    @model_validator(mode="after")
    def validate_effective_period(self) -> Self:
        """Ensure the policy end date is not before its start date."""
        if self.effective_to is not None and self.effective_to < self.effective_from:
            raise ValueError("effective_to must be on or after effective_from")

        return self
