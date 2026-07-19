from datetime import date
from pathlib import Path

import pytest

from policy_rag.domain.policy import PolicyClassification, PolicyDocument
from policy_rag.ingestion.sections import extract_policy_sections
from policy_rag.ingestion.source import PolicySourceDocument


def create_source(content: str) -> PolicySourceDocument:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees",),
    )

    return PolicySourceDocument(
        metadata=policy,
        content=content,
        content_path=Path("content.md"),
    )


def test_extract_policy_sections_preserves_order_and_metadata() -> None:
    source = create_source(
        """# Remote Working Policy

## 1. Purpose

Purpose content.

## 2. Scope

Scope content.
"""
    )

    sections = extract_policy_sections(source)

    assert len(sections) == 2

    assert sections[0].section_id == "POL-HR-001:1.0:SEC-001"
    assert sections[0].section_number == "1"
    assert sections[0].title == "Purpose"
    assert sections[0].content == "Purpose content."
    assert sections[0].ordinal == 1
    assert sections[0].heading_level == 2

    assert sections[1].section_id == "POL-HR-001:1.0:SEC-002"
    assert sections[1].section_number == "2"
    assert sections[1].title == "Scope"
    assert sections[1].ordinal == 2

    assert sections[0].policy is source.metadata


def test_extract_policy_sections_supports_nested_numbering() -> None:
    source = create_source(
        """# Remote Working Policy

## 1. Security

General security requirements.

### 1.1. Managed devices

Only managed devices may be used.
"""
    )

    sections = extract_policy_sections(source)

    assert len(sections) == 2
    assert sections[1].section_number == "1.1"
    assert sections[1].title == "Managed devices"
    assert sections[1].heading_level == 3


def test_extract_policy_sections_rejects_document_without_numbered_sections() -> None:
    source = create_source(
        """# Remote Working Policy

This document has no numbered sections.
"""
    )

    with pytest.raises(
        ValueError,
        match="no numbered policy sections found",
    ):
        extract_policy_sections(source)


def test_extract_policy_sections_rejects_empty_section() -> None:
    source = create_source(
        """# Remote Working Policy

## 1. Purpose

## 2. Scope

Scope content.
"""
    )

    with pytest.raises(
        ValueError,
        match="policy section 1 has no content",
    ):
        extract_policy_sections(source)
