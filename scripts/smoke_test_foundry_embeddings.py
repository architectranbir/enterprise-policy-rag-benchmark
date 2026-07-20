"""Verify keyless embedding inference against Microsoft Foundry."""

import json
import os

from azure.identity import DefaultAzureCredential

from policy_rag.embeddings import FoundryEmbeddingProvider

TEST_TEXT = "Enterprise policy retrieval smoke test."


def main() -> None:
    deployment = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
    credential = DefaultAzureCredential()
    provider = FoundryEmbeddingProvider(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=deployment,
        credential=credential,
    )

    try:
        vectors = provider.embed((TEST_TEXT,))
    finally:
        credential.close()

    print(
        json.dumps(
            {
                "model": deployment,
                "dimensions": len(vectors[0]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
