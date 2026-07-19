from collections.abc import Sequence

import tiktoken


class TokenCounter:
    """Encode, decode and count text tokens using a fixed encoding."""

    def __init__(self, encoding_name: str = "cl100k_base") -> None:
        self.encoding_name = encoding_name
        self._encoding: tiktoken.Encoding = tiktoken.get_encoding(encoding_name)

    def encode(self, text: str) -> tuple[int, ...]:
        """Encode text into an immutable token sequence."""
        return tuple(self._encoding.encode(text))

    def decode(self, tokens: Sequence[int]) -> str:
        """Decode a token sequence back into text."""
        return self._encoding.decode(list(tokens), errors="strict")

    def count(self, text: str) -> int:
        """Return the number of tokens in the supplied text."""
        return len(self._encoding.encode(text))
