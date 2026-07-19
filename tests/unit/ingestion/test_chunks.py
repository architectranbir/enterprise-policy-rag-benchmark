from datetime import date

from policy_rag.domain.policy import PolicyClassification, PolicyDocument
from policy_rag.domain.section import PolicySection
from policy_rag.ingestion.chunks import create_section_chunks


def create_section() -> PolicySection:
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
        content="Employees may claim up to GBP 250 once every three years.",
        ordinal=6,
        heading_level=2,
    )


def test_create_section_chunks_creates_one_chunk() -> None:
    section = create_section()

    chunks = create_section_chunks(section)

    assert len(chunks) == 1

    chunk = chunks[0]

    assert chunk.chunk_id == "POL-HR-001:1.0:SEC-006:CHK-001"
    assert chunk.content == section.content
    assert chunk.ordinal == 1
    assert chunk.section is section


def test_create_section_chunks_is_deterministic() -> None:
    section = create_section()

    first_result = create_section_chunks(section)
    second_result = create_section_chunks(section)

    assert first_result == second_result
