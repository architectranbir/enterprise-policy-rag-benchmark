from policy_rag.domain.chunking import ChunkingConfig
from policy_rag.ingestion.token_windows import create_token_windows


def test_create_token_windows_returns_empty_for_no_tokens() -> None:
    config = ChunkingConfig()

    assert create_token_windows((), config) == ()


def test_create_token_windows_keeps_short_content_in_one_window() -> None:
    config = ChunkingConfig(
        max_chunk_tokens=64,
        overlap_tokens=16,
    )
    tokens = tuple(range(20))

    windows = create_token_windows(tokens, config)

    assert windows == (tokens,)


def test_create_token_windows_splits_long_content_with_overlap() -> None:
    config = ChunkingConfig(
        max_chunk_tokens=512,
        overlap_tokens=128,
    )
    tokens = tuple(range(900))

    windows = create_token_windows(tokens, config)

    assert [len(window) for window in windows] == [512, 512, 132]
    assert windows[0][-128:] == windows[1][:128]
    assert windows[1][-128:] == windows[2][:128]


def test_create_token_windows_is_deterministic() -> None:
    config = ChunkingConfig(
        max_chunk_tokens=128,
        overlap_tokens=32,
    )
    tokens = tuple(range(300))

    assert create_token_windows(tokens, config) == create_token_windows(
        tokens,
        config,
    )
