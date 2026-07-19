from pathlib import Path

from policy_rag.domain.chunking import ChunkingConfig
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.sections import extract_policy_sections
from policy_rag.ingestion.source import load_policy_source
from policy_rag.ingestion.tokenizer import TokenCounter

POLICY_VERSION_DIRECTORY = Path("data/synthetic/policies/POL-HR-001/1.0")


def test_committed_policy_respects_default_chunking_limits() -> None:
    """Verify controlled chunking against the committed policy."""

    config = ChunkingConfig()
    counter = TokenCounter()

    source = load_policy_source(POLICY_VERSION_DIRECTORY)
    sections = extract_policy_sections(source)

    chunks = tuple(
        chunk
        for section in sections
        for chunk in create_section_chunks(
            section,
            config=config,
            token_counter=counter,
        )
    )

    assert len(sections) == 11
    assert len(chunks) == 11

    assert all(counter.count(chunk.content) <= config.max_chunk_tokens for chunk in chunks)

    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)

    assert chunks[0].chunk_id == ("POL-HR-001:1.0:SEC-001:CHK-001")
    assert chunks[-1].chunk_id == ("POL-HR-001:1.0:SEC-011:CHK-001")
