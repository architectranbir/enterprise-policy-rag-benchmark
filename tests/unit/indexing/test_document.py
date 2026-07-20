from datetime import date

from policy_rag.domain.chunk import PolicyChunk
from policy_rag.domain.policy import PolicyClassification, PolicyDocument
from policy_rag.domain.section import PolicySection
from policy_rag.indexing import policy_chunk_to_indexed_document
from policy_rag.ingestion.llamaindex_nodes import policy_chunk_to_text_node


def create_chunk() -> PolicyChunk:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "human-resources"),
    )
    section = PolicySection(
        section_id="POL-HR-001:1.0:SEC-006",
        policy=policy,
        section_number="6",
        title="Equipment and expenses",
        content="Employees may claim up to GBP 250.",
        ordinal=6,
        heading_level=2,
    )
    return PolicyChunk(
        chunk_id="POL-HR-001:1.0:SEC-006:CHK-001",
        section=section,
        content=section.content,
        ordinal=1,
    )


def test_chunk_maps_to_backend_neutral_indexed_document() -> None:
    chunk = create_chunk()

    document = policy_chunk_to_indexed_document(
        chunk,
        (0.1, 0.2, 0.3),
    )

    assert document.chunk_id == chunk.chunk_id
    assert document.embedding == (0.1, 0.2, 0.3)
    assert document.document_id == "POL-HR-001"
    assert document.version == "1.0"
    assert document.classification is PolicyClassification.INTERNAL
    assert document.allowed_groups == ("employees", "human-resources")
    assert document.section_id == "POL-HR-001:1.0:SEC-006"
    assert document.chunk_ordinal == 1


def test_indexed_document_and_llamaindex_node_share_identical_text() -> None:
    chunk = create_chunk()

    document = policy_chunk_to_indexed_document(chunk, (0.1,))
    node = policy_chunk_to_text_node(chunk)

    assert document.text == node.text
    assert document.text == (
        "Remote Working Policy\n"
        "Section 6: Equipment and expenses\n\n"
        "Employees may claim up to GBP 250."
    )
