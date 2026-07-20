from datetime import UTC, date, datetime

import pytest

from policy_rag.domain.policy import PolicyClassification
from policy_rag.indexing.azure_document import (
    azure_document_key,
    indexed_chunk_to_azure_document,
)
from policy_rag.indexing.azure_search import EMBEDDING_DIMENSIONS
from policy_rag.indexing.document import IndexedPolicyChunk


def create_document() -> IndexedPolicyChunk:
    return IndexedPolicyChunk(
        chunk_id="POL-HR-001:1.0:SEC-006:CHK-001",
        text=(
            "Remote Working Policy\n"
            "Section 6: Equipment and expenses\n\n"
            "Employees may claim up to GBP 250."
        ),
        embedding=(0.1,) * EMBEDDING_DIMENSIONS,
        document_id="POL-HR-001",
        document_title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        effective_to=None,
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "human-resources"),
        section_id="POL-HR-001:1.0:SEC-006",
        section_number="6",
        section_title="Equipment and expenses",
        section_ordinal=6,
        chunk_ordinal=1,
    )


def test_azure_document_key_is_deterministic_and_url_safe() -> None:
    chunk_id = "POL-HR-001:1.0:SEC-006:CHK-001"

    key = azure_document_key(chunk_id)

    assert key == azure_document_key(chunk_id)
    assert ":" not in key
    assert all(character.isalnum() or character in "_-=" for character in key)


def test_mapping_preserves_canonical_content_and_metadata() -> None:
    source = create_document()

    result = indexed_chunk_to_azure_document(source)

    assert result["id"] == azure_document_key(source.chunk_id)
    assert result["chunk_id"] == source.chunk_id
    assert result["text"] == source.text
    assert result["embedding"] == [0.1] * EMBEDDING_DIMENSIONS
    assert result["effective_from"] == datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )
    assert result["effective_to"] is None
    assert result["classification"] == "internal"
    assert result["allowed_groups"] == [
        "employees",
        "human-resources",
    ]
    assert result["section_id"] == source.section_id
    assert result["chunk_ordinal"] == 1


def test_mapping_rejects_embedding_dimension_mismatch() -> None:
    source = create_document().model_copy(
        update={"embedding": (0.1,)},
    )

    with pytest.raises(
        ValueError,
        match=r"Expected 3072 embedding dimensions, received 1",
    ):
        indexed_chunk_to_azure_document(source)
