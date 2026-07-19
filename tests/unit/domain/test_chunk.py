from datetime import date

import pytest
from pydantic import ValidationError

from policy_rag.domain.chunk import PolicyChunk
from policy_rag.domain.policy import PolicyClassification, PolicyDocument
from policy_rag.domain.section import PolicySection


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
        content="Employees may claim approved home-office expenses.",
        ordinal=6,
        heading_level=2,
    )


def test_policy_chunk_accepts_valid_data() -> None:
    chunk = PolicyChunk(
        chunk_id="POL-HR-001:1.0:SEC-006:CHK-001",
        section=create_section(),
        content="Employees may claim up to GBP 250.",
        ordinal=1,
    )

    assert chunk.chunk_id == "POL-HR-001:1.0:SEC-006:CHK-001"
    assert chunk.ordinal == 1
    assert chunk.section.section_number == "6"
    assert chunk.section.policy.version == "1.0"


def test_policy_chunk_strips_content_whitespace() -> None:
    chunk = PolicyChunk(
        chunk_id="POL-HR-001:1.0:SEC-006:CHK-001",
        section=create_section(),
        content="  Employees may claim up to GBP 250.  ",
        ordinal=1,
    )

    assert chunk.content == "Employees may claim up to GBP 250."


def test_policy_chunk_rejects_invalid_ordinal() -> None:
    with pytest.raises(ValidationError):
        PolicyChunk(
            chunk_id="POL-HR-001:1.0:SEC-006:CHK-001",
            section=create_section(),
            content="Synthetic chunk content.",
            ordinal=0,
        )


def test_policy_chunk_rejects_unknown_fields() -> None:
    data = {
        "chunk_id": "POL-HR-001:1.0:SEC-006:CHK-001",
        "section": create_section(),
        "content": "Synthetic chunk content.",
        "ordinal": 1,
        "backend_name": "unexpected",
    }

    with pytest.raises(ValidationError) as error:
        PolicyChunk.model_validate(data)

    assert "backend_name" in str(error.value)
