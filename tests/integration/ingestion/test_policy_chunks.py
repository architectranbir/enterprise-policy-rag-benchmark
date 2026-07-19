from pathlib import Path

from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.sections import extract_policy_sections
from policy_rag.ingestion.source import load_policy_source

POLICY_VERSION_DIRECTORY = Path("data/synthetic/policies/POL-HR-001/1.0")


def test_committed_policy_produces_deterministic_chunks() -> None:
    """Verify chunk creation from the committed synthetic policy."""

    source = load_policy_source(POLICY_VERSION_DIRECTORY)
    sections = extract_policy_sections(source)

    chunks = tuple(chunk for section in sections for chunk in create_section_chunks(section))

    assert len(chunks) == 11

    assert chunks[0].chunk_id == "POL-HR-001:1.0:SEC-001:CHK-001"
    assert chunks[0].section.title == "Purpose"

    equipment_chunk = chunks[5]
    assert equipment_chunk.chunk_id == ("POL-HR-001:1.0:SEC-006:CHK-001")
    assert equipment_chunk.section.title == "Equipment and expenses"
    assert "GBP 250" in equipment_chunk.content

    assert chunks[-1].chunk_id == ("POL-HR-001:1.0:SEC-011:CHK-001")

    assert all(
        chunk.section.policy.document_id == "POL-HR-001"
        and chunk.section.policy.version == "1.0"
        and chunk.section.policy.allowed_groups == ("employees", "human-resources")
        for chunk in chunks
    )
