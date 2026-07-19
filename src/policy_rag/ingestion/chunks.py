from policy_rag.domain.chunk import PolicyChunk
from policy_rag.domain.section import PolicySection


def create_section_chunks(
    section: PolicySection,
) -> tuple[PolicyChunk, ...]:
    """Create deterministic retrieval chunks for one policy section."""

    return (
        PolicyChunk(
            chunk_id=f"{section.section_id}:CHK-001",
            section=section,
            content=section.content,
            ordinal=1,
        ),
    )
