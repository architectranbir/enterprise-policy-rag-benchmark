from datetime import date

from policy_rag.domain.chunking import ChunkingConfig
from policy_rag.domain.policy import PolicyClassification, PolicyDocument
from policy_rag.domain.section import PolicySection
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.tokenizer import TokenCounter


def create_section(
    content: str = "Employees may claim up to GBP 250 once every three years.",
) -> PolicySection:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "human-resources"),
    )

    return PolicySection(
        section_id="POL-HR-001:1.0:SEC-006",
        policy=policy,
        section_number="6",
        title="Equipment and expenses",
        content=content,
        ordinal=6,
        heading_level=2,
    )


def test_create_section_chunks_keeps_short_section_in_one_chunk() -> None:
    section = create_section()

    chunks = create_section_chunks(section)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "POL-HR-001:1.0:SEC-006:CHK-001"
    assert chunks[0].content == section.content
    assert chunks[0].ordinal == 1
    assert chunks[0].section is section


def test_create_section_chunks_splits_long_section() -> None:
    section = create_section(
        content=("Remote working requires manager approval and secure access. " * 100).strip()
    )
    config = ChunkingConfig(
        max_chunk_tokens=64,
        overlap_tokens=16,
    )
    counter = TokenCounter()

    chunks = create_section_chunks(
        section,
        config=config,
        token_counter=counter,
    )

    assert len(chunks) > 1

    assert [chunk.ordinal for chunk in chunks] == list(range(1, len(chunks) + 1))

    assert chunks[0].chunk_id == "POL-HR-001:1.0:SEC-006:CHK-001"
    assert chunks[-1].chunk_id == (f"POL-HR-001:1.0:SEC-006:CHK-{len(chunks):03d}")

    assert all(counter.count(chunk.content) <= config.max_chunk_tokens for chunk in chunks)


def test_create_section_chunks_is_deterministic() -> None:
    section = create_section(content=("Synthetic policy requirement. " * 100).strip())
    config = ChunkingConfig(
        max_chunk_tokens=64,
        overlap_tokens=16,
    )
    counter = TokenCounter()

    first_result = create_section_chunks(
        section,
        config=config,
        token_counter=counter,
    )
    second_result = create_section_chunks(
        section,
        config=config,
        token_counter=counter,
    )

    assert first_result == second_result
