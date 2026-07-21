import json
from io import BytesIO
from unittest.mock import patch
from urllib.request import Request

import pytest

from policy_rag.embeddings import FoundryEmbeddingProvider


class StubAccessToken:
    token = "test-token"


class StubCredential:
    def __init__(self) -> None:
        self.scopes: tuple[str, ...] = ()

    def get_token(self, *scopes: str) -> StubAccessToken:
        self.scopes = scopes
        return StubAccessToken()


def test_embed_uses_entra_token_and_preserves_input_order() -> None:
    credential = StubCredential()
    response = BytesIO(
        json.dumps(
            {
                "data": [
                    {"index": 1, "embedding": [4.0, 5.0, 6.0]},
                    {"index": 0, "embedding": [1.0, 2.0, 3.0]},
                ]
            }
        ).encode()
    )

    with patch(
        "policy_rag.embeddings.foundry.urlopen",
        return_value=response,
    ) as open_request:
        provider = FoundryEmbeddingProvider(
            endpoint="https://example.openai.azure.com/",
            deployment="embedding deployment",
            credential=credential,
            dimensions=3,
        )

        vectors = provider.embed(("first", "second"))

    assert vectors == (
        (1.0, 2.0, 3.0),
        (4.0, 5.0, 6.0),
    )
    assert credential.scopes == ("https://cognitiveservices.azure.com/.default",)

    request = open_request.call_args.args[0]
    assert isinstance(request, Request)
    assert request.full_url == "https://example.openai.azure.com/openai/v1/embeddings"
    assert request.get_header("Authorization") == "Bearer test-token"

    request_body = request.data
    assert isinstance(request_body, bytes)
    assert json.loads(request_body) == {
        "model": "embedding deployment",
        "input": ["first", "second"],
        "dimensions": 3,
    }
    assert open_request.call_args.kwargs == {"timeout": 30}


def test_empty_batch_does_not_request_token_or_call_endpoint() -> None:
    credential = StubCredential()
    provider = FoundryEmbeddingProvider(
        endpoint="https://example.openai.azure.com",
        deployment="embedding",
        credential=credential,
    )

    with patch("policy_rag.embeddings.foundry.urlopen") as open_request:
        assert provider.embed(()) == ()

    assert credential.scopes == ()
    open_request.assert_not_called()


def test_rejects_blank_text() -> None:
    provider = FoundryEmbeddingProvider(
        endpoint="https://example.openai.azure.com",
        deployment="embedding",
        credential=StubCredential(),
    )

    with pytest.raises(ValueError, match="must not be empty"):
        provider.embed(("valid", " "))
