from datetime import date

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification, PolicyDocument
from policy_rag.domain.policy_access import can_retrieve_policy


def create_policy() -> PolicyDocument:
    return PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "hr"),
    )


def test_policy_can_be_retrieved_when_date_and_group_match() -> None:
    context = PolicyAccessContext(
        user_id="USER-001",
        user_groups=("employees",),
        as_of=date(2026, 7, 19),
    )

    assert can_retrieve_policy(create_policy(), context) is True


def test_policy_cannot_be_retrieved_outside_effective_period() -> None:
    context = PolicyAccessContext(
        user_id="USER-001",
        user_groups=("employees",),
        as_of=date(2027, 1, 1),
    )

    assert can_retrieve_policy(create_policy(), context) is False


def test_policy_cannot_be_retrieved_without_allowed_group() -> None:
    context = PolicyAccessContext(
        user_id="USER-002",
        user_groups=("contractors",),
        as_of=date(2026, 7, 19),
    )

    assert can_retrieve_policy(create_policy(), context) is False
