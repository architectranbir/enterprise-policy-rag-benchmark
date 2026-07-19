import pytest
from pydantic import ValidationError

from policy_rag.domain.chunking import ChunkingConfig


def test_chunking_config_uses_expected_defaults() -> None:
    config = ChunkingConfig()

    assert config.max_chunk_tokens == 512
    assert config.overlap_tokens == 128


def test_chunking_config_accepts_valid_custom_values() -> None:
    config = ChunkingConfig(
        max_chunk_tokens=768,
        overlap_tokens=128,
    )

    assert config.max_chunk_tokens == 768
    assert config.overlap_tokens == 128


@pytest.mark.parametrize(
    ("max_chunk_tokens", "overlap_tokens"),
    [
        (512, 256),
        (512, 300),
        (256, 128),
    ],
)
def test_chunking_config_rejects_excessive_overlap(
    max_chunk_tokens: int,
    overlap_tokens: int,
) -> None:
    with pytest.raises(
        ValidationError,
        match="overlap_tokens must be less than half",
    ):
        ChunkingConfig(
            max_chunk_tokens=max_chunk_tokens,
            overlap_tokens=overlap_tokens,
        )


def test_chunking_config_rejects_chunk_size_below_minimum() -> None:
    with pytest.raises(ValidationError):
        ChunkingConfig(
            max_chunk_tokens=32,
            overlap_tokens=0,
        )


def test_chunking_config_rejects_unknown_settings() -> None:
    with pytest.raises(ValidationError) as error:
        ChunkingConfig.model_validate(
            {
                "max_chunk_tokens": 512,
                "overlap_tokens": 128,
                "split_method": "unexpected",
            }
        )

    assert "split_method" in str(error.value)
