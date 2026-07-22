"""Keyless grounded generation through the stable Azure OpenAI REST API."""

import json
import time
from collections.abc import Sequence
from typing import Any, cast
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from policy_rag.embeddings.foundry import TOKEN_SCOPE, TokenCredential
from policy_rag.retrieval.models import RetrievedPolicyChunk

SYSTEM_PROMPT = """You answer enterprise policy questions only from the supplied evidence.
Use citation markers such as [1] after every supported claim. If the evidence does not answer
the question, reply exactly: I cannot answer this question from the available policy evidence."""


class FoundryAnswerProvider:
    def __init__(
        self,
        *,
        endpoint: str,
        deployment: str,
        credential: TokenCredential,
        timeout_seconds: float = 45,
        max_retries: int = 3,
        max_retry_delay_seconds: float = 60,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_retries < 0:
            raise ValueError("max_retries must not be negative")
        if max_retry_delay_seconds <= 0:
            raise ValueError("max_retry_delay_seconds must be positive")
        self._endpoint = endpoint.rstrip("/")
        self._deployment = deployment
        self._credential = credential
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._max_retry_delay_seconds = max_retry_delay_seconds

    def generate(self, question: str, evidence: Sequence[RetrievedPolicyChunk]) -> str:
        context = "\n\n".join(f"[{index}] {chunk.text}" for index, chunk in enumerate(evidence, 1))
        body = {
            "model": self._deployment,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Evidence:\n{context}\n\nQuestion: {question}"},
            ],
            "max_completion_tokens": 600,
        }
        request = Request(
            f"{self._endpoint}/openai/v1/chat/completions",
            data=json.dumps(body).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {self._credential.get_token(TOKEN_SCOPE).token}",
                "Content-Type": "application/json",
            },
        )
        payload: dict[str, Any] | None = None
        transient_statuses = {429, 500, 502, 503, 504}
        for attempt in range(self._max_retries + 1):
            try:
                with urlopen(request, timeout=self._timeout_seconds) as response:
                    payload = cast(dict[str, Any], json.load(response))
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
                raise RuntimeError(
                    f"Answer request failed with HTTP {error.code}: {error.read().decode()}"
                ) from error

        if payload is None:
            raise RuntimeError("Answer request exhausted retries without a response")
        choices = cast(list[dict[str, Any]], payload.get("choices", []))
        if not choices:
            raise RuntimeError("Answer response contained no choices")
        message = cast(dict[str, Any], choices[0]["message"])
        answer = str(message["content"]).strip()
        if not answer:
            raise RuntimeError("Answer response was empty")
        return answer
