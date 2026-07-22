import json
from email.message import Message
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from policy_rag.answering.foundry import FoundryAnswerProvider


class StubAccessToken:
    token = "test-token"


class StubCredential:
    def get_token(self, *scopes: str) -> StubAccessToken:
        return StubAccessToken()


def test_generate_retries_rate_limit_using_retry_after() -> None:
    headers = Message()
    headers["Retry-After"] = "3"
    rate_limit = HTTPError(
        "https://example.openai.azure.com/openai/v1/chat/completions",
        429,
        "Too Many Requests",
        headers,
        BytesIO(b'{"error":"rate limited"}'),
    )
    response = BytesIO(
        json.dumps({"choices": [{"message": {"content": "Grounded answer [1]"}}]}).encode()
    )
    provider = FoundryAnswerProvider(
        endpoint="https://example.openai.azure.com",
        deployment="answer",
        credential=StubCredential(),
    )

    with (
        patch(
            "policy_rag.answering.foundry.urlopen",
            side_effect=(rate_limit, response),
        ) as open_request,
        patch("policy_rag.answering.foundry.time.sleep") as sleep,
    ):
        assert provider.generate("question", ()) == "Grounded answer [1]"

    assert open_request.call_count == 2
    sleep.assert_called_once_with(3.0)
