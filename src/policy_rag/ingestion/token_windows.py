from collections.abc import Sequence

from policy_rag.domain.chunking import ChunkingConfig


def create_token_windows(
    tokens: Sequence[int],
    config: ChunkingConfig,
) -> tuple[tuple[int, ...], ...]:
    """Split tokens into deterministic overlapping windows."""

    if not tokens:
        return ()

    step_size = config.max_chunk_tokens - config.overlap_tokens

    return tuple(
        tuple(tokens[start : start + config.max_chunk_tokens])
        for start in range(0, len(tokens), step_size)
    )
