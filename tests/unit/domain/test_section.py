from datetime import date

import pytest
from pydantic import ValidationError

from policy_rag.domain.policy import PolicyClassification, PolicyDocument
from policy_rag.domain.section import PolicySection


def create_policy() -> PolicyDocument:
    return PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "human-resources"),
    )


def test_policy_section_accepts_valid_data() -> None:
    section = PolicySection(
        section_id="POL-HR-001:1.0:SEC-006",
        policy=create_policy(),
        section_number="6",
        title="Equipment and expenses",
        content="Employees may claim approved home-office expenses.",
        ordinal=6,
        heading_level=2,
    )

    assert section.section_number == "6"
    assert section.ordinal == 6
    assert section.policy.document_id == "POL-HR-001"


def test_policy_section_rejects_invalid_section_number() -> None:
    with pytest.raises(ValidationError):
        PolicySection(
            section_id="POL-HR-001:1.0:SEC-006",
            policy=create_policy(),
            section_number="Section 6",
            title="Equipment and expenses",
            content="Synthetic section content.",
            ordinal=6,
            heading_level=2,
        )


def test_policy_section_rejects_invalid_heading_level() -> None:
    with pytest.raises(ValidationError):
        PolicySection(
            section_id="POL-HR-001:1.0:SEC-006",
            policy=create_policy(),
            section_number="6",
            title="Equipment and expenses",
            content="Synthetic section content.",
            ordinal=6,
            heading_level=1,
        )


def test_policy_section_rejects_unknown_fields() -> None:
    data = {
        "section_id": "POL-HR-001:1.0:SEC-006",
        "policy": create_policy(),
        "section_number": "6",
        "title": "Equipment and expenses",
        "content": "Synthetic section content.",
        "ordinal": 6,
        "heading_level": 2,
        "page_owner": "unexpected",
    }

    with pytest.raises(ValidationError) as error:
        PolicySection.model_validate(data)

    assert "page_owner" in str(error.value)
