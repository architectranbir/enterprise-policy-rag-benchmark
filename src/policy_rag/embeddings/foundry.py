import json
import time
from collections.abc import Sequence
from typing import Any, Protocol, cast
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from policy_rag.embeddings.provider import EmbeddingVector

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
        max_retries: int = 3,
        max_retry_delay_seconds: float = 60,
    ) -> None:
        if not endpoint.strip():
            raise ValueError("endpoint must not be empty")
        if not deployment.strip():
            raise ValueError("deployment must not be empty")
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_retries < 0:
            raise ValueError("max_retries must not be negative")
        if max_retry_delay_seconds <= 0:
            raise ValueError("max_retry_delay_seconds must be positive")

        self._endpoint = endpoint.rstrip("/")
        self._deployment = deployment
        self._credential = credential
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._max_retry_delay_seconds = max_retry_delay_seconds

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, texts: Sequence[str], /) -> tuple[EmbeddingVector, ...]:
        if not texts:
            return ()

        if any(not text.strip() for text in texts):
            raise ValueError("embedding texts must not be empty")

        access_token = self._credential.get_token(TOKEN_SCOPE).token
        url = f"{self._endpoint}/openai/v1/embeddings"
        request = Request(
            url=url,
            data=json.dumps(
                {
                    "model": self._deployment,
                    "input": list(texts),
                    "dimensions": self._dimensions,
                }
            ).encode(),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        result: dict[str, Any] | None = None
        transient_statuses = {429, 500, 502, 503, 504}
        for attempt in range(self._max_retries + 1):
            try:
                with urlopen(request, timeout=self._timeout_seconds) as response:
                    result = cast(dict[str, Any], json.load(response))
                break
            except HTTPError as error:
                if error.code in transient_statuses and attempt < self._max_retries:
                    retry_after = error.headers.get("Retry-After")
                    try:
                        delay = float(retry_after) if retry_after is not None else 2**attempt
                    except ValueError:
                        delay = 2**attempt
                    time.sleep(min(delay, self._max_retry_delay_seconds))
                    continue

                message = error.read().decode()
                raise RuntimeError(
                    f"Embedding request failed with HTTP {error.code}: {message}"
                ) from error

        if result is None:
            raise RuntimeError("Embedding request exhausted retries without a response")

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
