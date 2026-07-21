"""Microsoft Entra bearer-token validation and identity extraction."""

from collections.abc import Mapping
from typing import Any, Protocol, cast

import jwt
from pydantic import BaseModel, ConfigDict, Field


class AuthenticatedIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    user_id: str = Field(min_length=1, max_length=200)
    user_groups: tuple[str, ...] = Field(min_length=1)


class TokenValidationError(ValueError):
    """Raised when a bearer token cannot establish a trusted identity."""


class TokenValidator(Protocol):
    def validate(self, token: str) -> AuthenticatedIdentity: ...


class SigningKeyClient(Protocol):
    def get_signing_key_from_jwt(self, token: str) -> Any: ...


class EntraTokenValidator:
    """Validate Entra v2 access tokens and extract immutable ACL groups."""

    def __init__(
        self,
        *,
        tenant_id: str,
        audience: str,
        signing_keys: SigningKeyClient | None = None,
    ) -> None:
        if not tenant_id.strip() or not audience.strip():
            raise ValueError("tenant_id and audience must not be empty")
        self._issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self._audience = audience
        self._signing_keys = signing_keys or jwt.PyJWKClient(
            f"{self._issuer}/discovery/v2.0/keys",
            cache_keys=True,
            lifespan=3600,
        )

    def validate(self, token: str) -> AuthenticatedIdentity:
        if not token.strip():
            raise TokenValidationError("bearer token must not be empty")
        try:
            signing_key = self._signing_keys.get_signing_key_from_jwt(token).key
            claims = cast(
                Mapping[str, Any],
                jwt.decode(
                    token,
                    signing_key,
                    algorithms=["RS256"],
                    audience=self._audience,
                    issuer=self._issuer,
                    options={"require": ["exp", "iat", "iss", "aud", "sub"]},
                ),
            )
        except (jwt.PyJWTError, OSError) as error:
            raise TokenValidationError("bearer token validation failed") from error

        claim_names = claims.get("_claim_names", {})
        if claim_names is not None and not isinstance(claim_names, Mapping):
            raise TokenValidationError("token contains invalid claim metadata")
        if isinstance(claim_names, Mapping) and "groups" in claim_names:
            raise TokenValidationError("token contains group overage claims")

        raw_groups = claims.get("groups")
        if not isinstance(raw_groups, list) or not all(
            isinstance(group, str) and group.strip() for group in raw_groups
        ):
            raise TokenValidationError("token does not contain valid group claims")

        user_id = claims.get("oid") or claims.get("sub")
        if not isinstance(user_id, str) or not user_id.strip():
            raise TokenValidationError("token does not contain a valid user identifier")

        return AuthenticatedIdentity(user_id=user_id, user_groups=tuple(raw_groups))


def bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise TokenValidationError("Authorization header is required")
    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token.strip():
        raise TokenValidationError("Authorization header must use the Bearer scheme")
    return token.strip()
