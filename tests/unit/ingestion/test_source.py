import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from policy_rag.ingestion.source import load_policy_source


def write_policy_source(
    version_directory: Path,
    *,
    classification: str = "internal",
    content_heading: str = "# Remote Working Policy",
    include_content: bool = True,
) -> None:
    """Create a policy source directory for a unit test."""

    version_directory.mkdir(parents=True)

    metadata: dict[str, object] = {
        "document_id": "POL-HR-001",
        "title": "Remote Working Policy",
        "version": "1.0",
        "effective_from": "2026-01-01",
        "effective_to": None,
        "department": "Human Resources",
        "classification": classification,
        "allowed_groups": ["employees", "human-resources"],
    }

    metadata_path = version_directory / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    if include_content:
        content_path = version_directory / "content.md"
        content_path.write_text(
            f"{content_heading}\n\nThis is synthetic policy content.\n",
            encoding="utf-8",
        )


def test_load_policy_source_accepts_valid_files(tmp_path: Path) -> None:
    version_directory = tmp_path / "POL-HR-001" / "1.0"
    write_policy_source(version_directory)

    source = load_policy_source(version_directory)

    assert source.metadata.document_id == "POL-HR-001"
    assert source.metadata.version == "1.0"
    assert source.content.startswith("# Remote Working Policy")
    assert source.content_path == version_directory / "content.md"


def test_load_policy_source_rejects_invalid_metadata(tmp_path: Path) -> None:
    version_directory = tmp_path / "POL-HR-001" / "1.0"
    write_policy_source(
        version_directory,
        classification="secret",
    )

    with pytest.raises(ValidationError):
        load_policy_source(version_directory)


def test_load_policy_source_rejects_heading_mismatch(tmp_path: Path) -> None:
    version_directory = tmp_path / "POL-HR-001" / "1.0"
    write_policy_source(
        version_directory,
        content_heading="# Incorrect Policy Title",
    )

    with pytest.raises(
        ValueError,
        match="policy content must start with heading",
    ):
        load_policy_source(version_directory)


def test_load_policy_source_rejects_missing_content(tmp_path: Path) -> None:
    version_directory = tmp_path / "POL-HR-001" / "1.0"
    write_policy_source(
        version_directory,
        include_content=False,
    )

    with pytest.raises(FileNotFoundError, match="content.md"):
        load_policy_source(version_directory)
