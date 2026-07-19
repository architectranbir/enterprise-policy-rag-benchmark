from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChunkingConfig(BaseModel):
    """Validated settings for deterministic token-based chunking."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    max_chunk_tokens: int = Field(default=512, ge=64, le=8192)
    overlap_tokens: int = Field(default=128, ge=0)

    @model_validator(mode="after")
    def validate_overlap(self) -> Self:
        """Ensure overlap remains smaller than half of the chunk size."""

        if self.overlap_tokens * 2 >= self.max_chunk_tokens:
            raise ValueError("overlap_tokens must be less than half of max_chunk_tokens")

        return self
