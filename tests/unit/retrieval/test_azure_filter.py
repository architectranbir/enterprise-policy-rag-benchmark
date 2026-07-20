from datetime import date

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification
from policy_rag.retrieval import PolicyRetrievalRequest
from policy_rag.retrieval.azure_filter import build_azure_exact_filter


def create_request(
    *,
    user_groups: tuple[str, ...] = (
        "employees",
        "human-resources",
    ),
    department: str | None = "Human Resources",
) -> PolicyRetrievalRequest:
    return PolicyRetrievalRequest(
        access=PolicyAccessContext(
            user_id="USER-001",
            user_groups=user_groups,
            as_of=date(2026, 7, 20),
        ),
        document_id="POL-HR-001",
        department=department,
        classification=PolicyClassification.INTERNAL,
        limit=5,
    )


def test_builds_effective_acl_and_exact_metadata_filter() -> None:
    result = build_azure_exact_filter(create_request())

    assert result == (
        "effective_from le 2026-07-20T00:00:00Z"
        " and (effective_to eq null or "
        "effective_to ge 2026-07-20T00:00:00Z)"
        " and (allowed_groups/any(group: group eq 'employees')"
        " or allowed_groups/any(group: "
        "group eq 'human-resources'))"
        " and document_id eq 'POL-HR-001'"
        " and department eq 'Human Resources'"
        " and classification eq 'internal'"
    )


def test_escapes_quotes_in_group_and_metadata_values() -> None:
    request = create_request(
        user_groups=("manager's-team",),
        department="People's Operations",
    )

    result = build_azure_exact_filter(request)

    assert "group eq 'manager''s-team'" in result
    assert "department eq 'People''s Operations'" in result


def test_empty_user_groups_builds_fail_closed_filter() -> None:
    request = create_request(user_groups=())

    assert build_azure_exact_filter(request) == "false"
