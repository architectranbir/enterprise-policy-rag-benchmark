from llama_index.core.schema import TextNode

from policy_rag.domain.chunk import PolicyChunk
from policy_rag.ingestion.chunk_text import policy_chunk_text


def policy_chunk_to_text_node(chunk: PolicyChunk) -> TextNode:
    """Convert a canonical policy chunk into a LlamaIndex text node."""

    policy = chunk.section.policy

    metadata: dict[str, str | int | list[str]] = {
        "document_id": policy.document_id,
        "document_title": policy.title,
        "version": policy.version,
        "effective_from": policy.effective_from.isoformat(),
        "department": policy.department,
        "classification": policy.classification.value,
        "allowed_groups": list(policy.allowed_groups),
        "section_id": chunk.section.section_id,
        "section_number": chunk.section.section_number,
        "section_title": chunk.section.title,
        "section_ordinal": chunk.section.ordinal,
        "chunk_ordinal": chunk.ordinal,
    }

    if policy.effective_to is not None:
        metadata["effective_to"] = policy.effective_to.isoformat()

    return TextNode(
        id_=chunk.chunk_id,
        text=policy_chunk_text(chunk),
        metadata=metadata,
        excluded_embed_metadata_keys=list(metadata),
        excluded_llm_metadata_keys=["allowed_groups"],
    )
