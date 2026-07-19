from pathlib import Path

from policy_rag.ingestion.sections import extract_policy_sections
from policy_rag.ingestion.source import load_policy_source

POLICY_VERSION_DIRECTORY = Path("data/synthetic/policies/POL-HR-001/1.0")


def test_committed_policy_sections_are_extracted_correctly() -> None:
    """Verify section extraction from the committed synthetic policy."""

    source = load_policy_source(POLICY_VERSION_DIRECTORY)
    sections = extract_policy_sections(source)

    assert len(sections) == 11

    assert [section.section_number for section in sections] == [
        str(number) for number in range(1, 12)
    ]

    assert sections[0].section_id == "POL-HR-001:1.0:SEC-001"
    assert sections[0].title == "Purpose"

    equipment_section = sections[5]
    assert equipment_section.section_number == "6"
    assert equipment_section.title == "Equipment and expenses"
    assert "GBP 250" in equipment_section.content

    assert sections[-1].section_id == "POL-HR-001:1.0:SEC-011"
    assert sections[-1].title == "Policy review"

    assert all(
        section.policy.document_id == "POL-HR-001" and section.policy.version == "1.0"
        for section in sections
    )
