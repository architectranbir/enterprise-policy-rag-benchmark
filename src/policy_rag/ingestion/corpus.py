from pathlib import Path

from policy_rag.ingestion.source import (
    PolicySourceDocument,
    load_policy_source,
)


def load_policy_corpus(corpus_root: Path) -> tuple[PolicySourceDocument, ...]:
    """Discover, load and validate every policy version in a corpus."""

    metadata_paths = sorted(corpus_root.rglob("metadata.json"))

    if not metadata_paths:
        raise ValueError(f"no policy documents found under: {corpus_root}")

    documents: list[PolicySourceDocument] = []
    seen_versions: set[tuple[str, str]] = set()

    for metadata_path in metadata_paths:
        source = load_policy_source(metadata_path.parent)
        version_key = (
            source.metadata.document_id,
            source.metadata.version,
        )

        if version_key in seen_versions:
            document_id, version = version_key
            raise ValueError(f"duplicate policy version found: {document_id} version {version}")

        seen_versions.add(version_key)
        documents.append(source)

    return tuple(documents)
