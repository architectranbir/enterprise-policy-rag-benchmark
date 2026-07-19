from datetime import date

import pytest
from pydantic import ValidationError

from policy_rag.domain.access import PolicyAccessContext


def test_access_context_accepts_valid_data() -> None:
    context = PolicyAccessContext(
        user_id="USER-001",
        user_groups=("employees", "technology"),
        as_of=date(2026, 7, 19),
    )

    assert context.user_id == "USER-001"
    assert context.user_groups == ("employees", "technology")
    assert context.as_of == date(2026, 7, 19)


def test_access_context_strips_user_id_whitespace() -> None:
    context = PolicyAccessContext(
        user_id="  USER-001  ",
        user_groups=("employees",),
        as_of=date(2026, 7, 19),
    )

    assert context.user_id == "USER-001"


def test_access_context_allows_user_with_no_groups() -> None:
    context = PolicyAccessContext(
        user_id="USER-002",
        user_groups=(),
        as_of=date(2026, 7, 19),
    )

    assert context.user_groups == ()


def test_access_context_rejects_empty_user_id() -> None:
    with pytest.raises(ValidationError):
        PolicyAccessContext(
            user_id="",
            user_groups=("employees",),
            as_of=date(2026, 7, 19),
        )


def test_access_context_rejects_unknown_fields() -> None:
    data = {
        "user_id": "USER-001",
        "user_groups": ["employees"],
        "as_of": date(2026, 7, 19),
        "tenant_name": "unexpected",
    }

    with pytest.raises(ValidationError) as error:
        PolicyAccessContext.model_validate(data)

    assert "tenant_name" in str(error.value)
