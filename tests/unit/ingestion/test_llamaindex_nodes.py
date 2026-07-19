from datetime import date

from llama_index.core.schema import MetadataMode

from policy_rag.domain.chunk import PolicyChunk
from policy_rag.domain.policy import PolicyClassification, PolicyDocument
from policy_rag.domain.section import PolicySection
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


def test_policy_chunk_maps_to_deterministic_text_node() -> None:
    chunk = create_chunk()

    node = policy_chunk_to_text_node(chunk)

    assert node.node_id == chunk.chunk_id
    assert node.text == (
        "Remote Working Policy\n"
        "Section 6: Equipment and expenses\n\n"
        "Employees may claim up to GBP 250."
    )


def test_text_node_contains_filter_and_citation_metadata() -> None:
    node = policy_chunk_to_text_node(create_chunk())

    assert node.metadata["document_id"] == "POL-HR-001"
    assert node.metadata["version"] == "1.0"
    assert node.metadata["classification"] == "internal"
    assert node.metadata["allowed_groups"] == [
        "employees",
        "human-resources",
    ]
    assert node.metadata["section_number"] == "6"
    assert node.metadata["chunk_ordinal"] == 1


def test_operational_metadata_is_excluded_from_embedding_text() -> None:
    node = policy_chunk_to_text_node(create_chunk())

    assert node.get_metadata_str(MetadataMode.EMBED) == ""


def test_acl_metadata_is_excluded_from_llm_metadata() -> None:
    node = policy_chunk_to_text_node(create_chunk())

    llm_metadata = node.get_metadata_str(MetadataMode.LLM)

    assert "allowed_groups" not in llm_metadata
    assert "document_id" in llm_metadata
