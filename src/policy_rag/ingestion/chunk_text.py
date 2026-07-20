from policy_rag.domain.chunk import PolicyChunk


def policy_chunk_text(chunk: PolicyChunk) -> str:
    """Build the deterministic text shared by embedding and retrieval backends."""

    policy = chunk.section.policy

    return (
        f"{policy.title}\n"
        f"Section {chunk.section.section_number}: {chunk.section.title}\n\n"
        f"{chunk.content}"
    )
