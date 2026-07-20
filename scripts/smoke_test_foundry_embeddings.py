"""Verify keyless embedding inference against Microsoft Foundry."""

import json
import os
from typing import Any, cast
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from azure.identity import DefaultAzureCredential

API_VERSION = "2024-10-21"
TOKEN_SCOPE = "https://cognitiveservices.azure.com/.default"
TEST_TEXT = "Enterprise policy retrieval smoke test."


def main() -> None:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    deployment = quote(
        os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
        safe="",
    )

    credential = DefaultAzureCredential()

    try:
        access_token = credential.get_token(TOKEN_SCOPE).token
    finally:
        credential.close()

    url = f"{endpoint}/openai/deployments/{deployment}/embeddings?api-version={API_VERSION}"

    request = Request(
        url=url,
        data=json.dumps({"input": [TEST_TEXT]}).encode(),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            result = cast(dict[str, Any], json.load(response))
    except HTTPError as error:
        message = error.read().decode()
        raise RuntimeError(f"Embedding request failed with HTTP {error.code}: {message}") from error

    embedding = result["data"][0]["embedding"]
    usage = result["usage"]

    print(
        json.dumps(
            {
                "model": result["model"],
                "dimensions": len(embedding),
                "prompt_tokens": usage["prompt_tokens"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
