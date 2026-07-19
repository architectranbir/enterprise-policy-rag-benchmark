from policy_rag.domain.chunk import PolicyChunk
from policy_rag.domain.chunking import ChunkingConfig
from policy_rag.domain.section import PolicySection
from policy_rag.ingestion.token_windows import create_token_windows
from policy_rag.ingestion.tokenizer import TokenCounter


def create_section_chunks(
    section: PolicySection,
    *,
    config: ChunkingConfig | None = None,
    token_counter: TokenCounter | None = None,
) -> tuple[PolicyChunk, ...]:
    """Create deterministic token-aware chunks for one policy section."""

    resolved_config = config or ChunkingConfig()
    resolved_counter = token_counter or TokenCounter()

    tokens = resolved_counter.encode(section.content)
    token_windows = create_token_windows(tokens, resolved_config)

    chunks: list[PolicyChunk] = []

    for ordinal, token_window in enumerate(token_windows, start=1):
        chunk_content = resolved_counter.decode(token_window).strip()

        if not chunk_content:
            raise ValueError(f"chunk {ordinal} for section {section.section_id} is empty")

        chunks.append(
            PolicyChunk(
                chunk_id=f"{section.section_id}:CHK-{ordinal:03d}",
                section=section,
                content=chunk_content,
                ordinal=ordinal,
            )
        )

    return tuple(chunks)
