from datetime import date

import pytest
from pydantic import ValidationError

from policy_rag.domain.policy import PolicyClassification, PolicyDocument


def test_policy_document_accepts_valid_metadata() -> None:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "hr"),
    )

    assert policy.document_id == "POL-HR-001"
    assert policy.classification is PolicyClassification.INTERNAL
    assert policy.effective_to is None
    assert policy.allowed_groups == ("employees", "hr")


def test_policy_document_rejects_invalid_effective_period() -> None:
    with pytest.raises(
        ValidationError,
        match="effective_to must be on or after effective_from",
    ):
        PolicyDocument(
            document_id="POL-HR-001",
            title="Remote Working Policy",
            version="1.0",
            effective_from=date(2026, 1, 1),
            effective_to=date(2025, 12, 31),
            department="Human Resources",
            classification=PolicyClassification.INTERNAL,
            allowed_groups=("employees",),
        )


def test_policy_document_rejects_unknown_metadata() -> None:
    metadata = {
        "document_id": "POL-HR-001",
        "title": "Remote Working Policy",
        "version": "1.0",
        "effective_from": date(2026, 1, 1),
        "department": "Human Resources",
        "classification": "internal",
        "allowed_groups": ["employees"],
        "unknown_field": "unexpected",
    }

    with pytest.raises(ValidationError) as error:
        PolicyDocument.model_validate(metadata)

    assert "unknown_field" in str(error.value)


@pytest.mark.parametrize(
    ("as_of", "expected"),
    [
        (date(2025, 12, 31), False),
        (date(2026, 1, 1), True),
        (date(2026, 12, 31), True),
        (date(2027, 1, 1), False),
    ],
)
def test_policy_document_checks_effective_date(
    as_of: date,
    expected: bool,
) -> None:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees",),
    )

    assert policy.is_effective_on(as_of) is expected


def test_policy_document_supports_open_ended_effective_period() -> None:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="2.0",
        effective_from=date(2027, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees",),
    )

    assert policy.is_effective_on(date(2030, 1, 1)) is True


def test_policy_document_allows_user_with_matching_group() -> None:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "hr"),
    )

    assert policy.is_accessible_to({"employees", "technology"}) is True


def test_policy_document_denies_user_without_matching_group() -> None:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "hr"),
    )

    assert policy.is_accessible_to({"contractors", "suppliers"}) is False


def test_policy_document_denies_user_with_no_groups() -> None:
    policy = PolicyDocument(
        document_id="POL-HR-001",
        title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees",),
    )

    assert policy.is_accessible_to(set()) is False
