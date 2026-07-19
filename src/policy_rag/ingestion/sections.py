import re

from policy_rag.domain.section import PolicySection
from policy_rag.ingestion.source import PolicySourceDocument

_SECTION_HEADING_PATTERN = re.compile(
    r"^ {0,3}(?P<hashes>#{2,6})[ \t]+"
    r"(?P<number>\d+(?:\.\d+)*)\.[ \t]+"
    r"(?P<title>.+?)(?:[ \t]+#+)?[ \t]*$"
)


def extract_policy_sections(
    source: PolicySourceDocument,
) -> tuple[PolicySection, ...]:
    """Extract numbered Markdown sections from a validated policy source."""

    sections: list[PolicySection] = []
    current_number: str | None = None
    current_title: str | None = None
    current_heading_level: int | None = None
    current_content_lines: list[str] = []

    def flush_section() -> None:
        nonlocal current_number
        nonlocal current_title
        nonlocal current_heading_level
        nonlocal current_content_lines

        if current_number is None:
            return

        assert current_title is not None
        assert current_heading_level is not None

        content = "\n".join(current_content_lines).strip()

        if not content:
            raise ValueError(f"policy section {current_number} has no content")

        ordinal = len(sections) + 1

        sections.append(
            PolicySection(
                section_id=(
                    f"{source.metadata.document_id}:{source.metadata.version}:SEC-{ordinal:03d}"
                ),
                policy=source.metadata,
                section_number=current_number,
                title=current_title,
                content=content,
                ordinal=ordinal,
                heading_level=current_heading_level,
            )
        )

        current_number = None
        current_title = None
        current_heading_level = None
        current_content_lines = []

    for line in source.content.splitlines():
        heading_match = _SECTION_HEADING_PATTERN.match(line)

        if heading_match is not None:
            flush_section()

            current_number = heading_match.group("number")
            current_title = heading_match.group("title").strip()
            current_heading_level = len(heading_match.group("hashes"))
            continue

        if current_number is not None:
            current_content_lines.append(line)

    flush_section()

    if not sections:
        raise ValueError(f"no numbered policy sections found in: {source.content_path}")

    return tuple(sections)
