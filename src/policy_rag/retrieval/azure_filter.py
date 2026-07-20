"""Build Azure AI Search filters from backend-neutral retrieval requests."""

from policy_rag.retrieval.models import PolicyRetrievalRequest


def escape_odata_string(value: str) -> str:
    """Escape one OData string literal value."""

    return value.replace("'", "''")


def quote_odata_string(value: str) -> str:
    """Return one safely quoted OData string literal."""

    return f"'{escape_odata_string(value)}'"


def build_azure_exact_filter(request: PolicyRetrievalRequest) -> str:
    """Build deterministic effective-date, ACL, and metadata filters."""

    if not request.access.user_groups:
        return "false"

    as_of = f"{request.access.as_of.isoformat()}T00:00:00Z"

    group_filters = " or ".join(
        (f"allowed_groups/any(group: group eq {quote_odata_string(group)})")
        for group in request.access.user_groups
    )

    clauses = [
        f"effective_from le {as_of}",
        f"(effective_to eq null or effective_to ge {as_of})",
        f"({group_filters})",
    ]

    if request.document_id is not None:
        clauses.append(f"document_id eq {quote_odata_string(request.document_id)}")

    if request.department is not None:
        clauses.append(f"department eq {quote_odata_string(request.department)}")

    if request.classification is not None:
        clauses.append(f"classification eq {quote_odata_string(request.classification.value)}")

    return " and ".join(clauses)
