import json
from collections.abc import Sequence
from typing import Any, Protocol, cast
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from policy_rag.embeddings.provider import EmbeddingVector

API_VERSION = "2024-10-21"
TOKEN_SCOPE = "https://cognitiveservices.azure.com/.default"


class AccessToken(Protocol):
    @property
    def token(self) -> str:
        """Return the bearer token value."""
        ...


class TokenCredential(Protocol):
    def get_token(self, *scopes: str) -> AccessToken:
        """Acquire an access token for the requested scopes."""
        ...


class FoundryEmbeddingProvider:
    """Generate embeddings through the stable Foundry Azure OpenAI REST API."""

    def __init__(
        self,
        *,
        endpoint: str,
        deployment: str,
        credential: TokenCredential,
        dimensions: int = 3072,
        timeout_seconds: float = 30,
    ) -> None:
        if not endpoint.strip():
            raise ValueError("endpoint must not be empty")
        if not deployment.strip():
            raise ValueError("deployment must not be empty")
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self._endpoint = endpoint.rstrip("/")
        self._deployment = quote(deployment, safe="")
        self._credential = credential
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, texts: Sequence[str], /) -> tuple[EmbeddingVector, ...]:
        if not texts:
            return ()

        if any(not text.strip() for text in texts):
            raise ValueError("embedding texts must not be empty")

        access_token = self._credential.get_token(TOKEN_SCOPE).token
        url = (
            f"{self._endpoint}/openai/deployments/{self._deployment}/embeddings"
            f"?api-version={API_VERSION}"
        )
        request = Request(
            url=url,
            data=json.dumps({"input": list(texts)}).encode(),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                result = cast(dict[str, Any], json.load(response))
        except HTTPError as error:
            message = error.read().decode()
            raise RuntimeError(
                f"Embedding request failed with HTTP {error.code}: {message}"
            ) from error

        items = cast(list[dict[str, Any]], result["data"])
        ordered_items = sorted(items, key=lambda item: cast(int, item["index"]))

        if len(ordered_items) != len(texts):
            raise RuntimeError("Embedding response count does not match request count")

        vectors = tuple(
            tuple(float(value) for value in cast(list[float], item["embedding"]))
            for item in ordered_items
        )

        if any(len(vector) != self._dimensions for vector in vectors):
            raise RuntimeError(f"Embedding response did not contain {self._dimensions} dimensions")

        return vectors
