import json
from pathlib import Path

import pytest

from policy_rag.ingestion.corpus import load_policy_corpus


def write_policy_version(
    version_directory: Path,
    *,
    document_id: str,
    title: str,
    version: str = "1.0",
) -> None:
    """Create one valid synthetic policy version for a unit test."""

    version_directory.mkdir(parents=True)

    metadata: dict[str, object] = {
        "document_id": document_id,
        "title": title,
        "version": version,
        "effective_from": "2026-01-01",
        "effective_to": None,
        "department": "Policy Operations",
        "classification": "internal",
        "allowed_groups": ["employees"],
    }

    (version_directory / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    (version_directory / "content.md").write_text(
        f"# {title}\n\nSynthetic policy content.\n",
        encoding="utf-8",
    )


def test_load_policy_corpus_returns_documents_in_stable_order(
    tmp_path: Path,
) -> None:
    write_policy_version(
        tmp_path / "POL-HR-002" / "1.0",
        document_id="POL-HR-002",
        title="Leave Policy",
    )
    write_policy_version(
        tmp_path / "POL-HR-001" / "1.0",
        document_id="POL-HR-001",
        title="Remote Working Policy",
    )

    corpus = load_policy_corpus(tmp_path)

    assert [item.metadata.document_id for item in corpus] == [
        "POL-HR-001",
        "POL-HR-002",
    ]


def test_load_policy_corpus_rejects_empty_corpus(tmp_path: Path) -> None:
    with pytest.raises(
        ValueError,
        match="no policy documents found",
    ):
        load_policy_corpus(tmp_path)


def test_load_policy_corpus_rejects_duplicate_version(
    tmp_path: Path,
) -> None:
    write_policy_version(
        tmp_path / "copy-a" / "1.0",
        document_id="POL-HR-001",
        title="Remote Working Policy",
    )
    write_policy_version(
        tmp_path / "copy-b" / "1.0",
        document_id="POL-HR-001",
        title="Remote Working Policy",
    )

    with pytest.raises(
        ValueError,
        match="duplicate policy version found: POL-HR-001 version 1.0",
    ):
        load_policy_corpus(tmp_path)
