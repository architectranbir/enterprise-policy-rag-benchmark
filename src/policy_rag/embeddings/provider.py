from collections.abc import Sequence
from typing import Protocol

type EmbeddingVector = tuple[float, ...]


class EmbeddingProvider(Protocol):
    """Generate ordered embedding vectors without exposing provider details."""

    @property
    def dimensions(self) -> int:
        """Return the number of dimensions in every generated vector."""
        ...

    def embed(self, texts: Sequence[str], /) -> tuple[EmbeddingVector, ...]:
        """Embed texts in input order."""
        ...
