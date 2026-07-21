from typing import Any
from unittest.mock import patch

import pytest

from policy_rag.auth import EntraTokenValidator, TokenValidationError, bearer_token


class SigningKey:
    key = "public-key"


class SigningKeys:
    def get_signing_key_from_jwt(self, token: str) -> SigningKey:
        assert token == "signed-token"
        return SigningKey()


def validator() -> EntraTokenValidator:
    return EntraTokenValidator(
        tenant_id="tenant-id",
        audience="api://policy-rag",
        signing_keys=SigningKeys(),
    )


def claims(**updates: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "sub": "subject-id",
        "oid": "object-id",
        "groups": ["employees", "human-resources"],
    }
    values.update(updates)
    return values


def test_validates_signature_contract_and_extracts_identity() -> None:
    with patch("policy_rag.auth.jwt.decode", return_value=claims()) as decode:
        identity = validator().validate("signed-token")

    assert identity.user_id == "object-id"
    assert identity.user_groups == ("employees", "human-resources")
    assert decode.call_args.kwargs["audience"] == "api://policy-rag"
    assert decode.call_args.kwargs["issuer"] == ("https://login.microsoftonline.com/tenant-id/v2.0")
    assert decode.call_args.kwargs["algorithms"] == ["RS256"]


def test_rejects_group_overage_instead_of_bypassing_acl_resolution() -> None:
    overage = claims(_claim_names={"groups": "src1"})
    with patch("policy_rag.auth.jwt.decode", return_value=overage):
        with pytest.raises(TokenValidationError, match="overage"):
            validator().validate("signed-token")


def test_rejects_token_without_groups() -> None:
    with patch("policy_rag.auth.jwt.decode", return_value=claims(groups=None)):
        with pytest.raises(TokenValidationError, match="group claims"):
            validator().validate("signed-token")


def test_rejects_malformed_claim_metadata() -> None:
    with patch("policy_rag.auth.jwt.decode", return_value=claims(_claim_names="invalid")):
        with pytest.raises(TokenValidationError, match="claim metadata"):
            validator().validate("signed-token")


@pytest.mark.parametrize("value", [None, "", "Basic abc", "Bearer "])
def test_requires_well_formed_bearer_header(value: str | None) -> None:
    with pytest.raises(TokenValidationError):
        bearer_token(value)
