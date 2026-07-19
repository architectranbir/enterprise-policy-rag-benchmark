from pathlib import Path

from llama_index.core.schema import MetadataMode

from policy_rag.domain.chunking import ChunkingConfig
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.llamaindex_nodes import policy_chunk_to_text_node
from policy_rag.ingestion.sections import extract_policy_sections
from policy_rag.ingestion.source import load_policy_source
from policy_rag.ingestion.tokenizer import TokenCounter

POLICY_VERSION_DIRECTORY = Path("data/synthetic/policies/POL-HR-001/1.0")


def test_committed_policy_maps_to_deterministic_llamaindex_nodes() -> None:
    source = load_policy_source(POLICY_VERSION_DIRECTORY)
    sections = extract_policy_sections(source)

    config = ChunkingConfig()
    counter = TokenCounter()

    chunks = tuple(
        chunk
        for section in sections
        for chunk in create_section_chunks(
            section,
            config=config,
            token_counter=counter,
        )
    )

    nodes = tuple(policy_chunk_to_text_node(chunk) for chunk in chunks)

    assert len(nodes) == 11
    assert len({node.node_id for node in nodes}) == len(nodes)

    first_node = nodes[0]
    assert first_node.node_id == "POL-HR-001:1.0:SEC-001:CHK-001"
    assert first_node.metadata["document_id"] == "POL-HR-001"
    assert first_node.metadata["version"] == "1.0"
    assert first_node.metadata["section_number"] == "1"
    assert first_node.metadata["allowed_groups"] == [
        "employees",
        "human-resources",
    ]

    equipment_node = nodes[5]
    assert equipment_node.node_id == ("POL-HR-001:1.0:SEC-006:CHK-001")
    assert equipment_node.metadata["section_title"] == ("Equipment and expenses")
    assert "GBP 250" in equipment_node.text

    assert all(node.embedding is None for node in nodes)
    assert all(node.get_metadata_str(MetadataMode.EMBED) == "" for node in nodes)
