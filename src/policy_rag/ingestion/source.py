from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from policy_rag.domain.policy import PolicyDocument


class PolicySourceDocument(BaseModel):
    """Validated policy metadata together with its source content."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    metadata: PolicyDocument
    content: str = Field(min_length=1)
    content_path: Path


def load_policy_source(version_directory: Path) -> PolicySourceDocument:
    """Load and validate one policy version from its source directory."""

    metadata_path = version_directory / "metadata.json"
    content_path = version_directory / "content.md"

    metadata = PolicyDocument.model_validate_json(metadata_path.read_text(encoding="utf-8"))
    content = content_path.read_text(encoding="utf-8").strip()

    expected_heading = f"# {metadata.title}"
    if not content.startswith(expected_heading):
        raise ValueError(f"policy content must start with heading: {expected_heading}")

    return PolicySourceDocument(
        metadata=metadata,
        content=content,
        content_path=content_path,
    )
