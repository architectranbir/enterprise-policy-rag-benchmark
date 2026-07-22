"""Verify keyless Azure AI Search index creation and schema retrieval."""

import json
import os

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient

from policy_rag.indexing.azure_search import (
    AZURE_SEARCH_API_VERSION,
    EMBEDDING_DIMENSIONS,
    create_policy_chunk_search_index,
)

DEFAULT_INDEX_NAME = "policy-chunks-dev-v1"


def main() -> None:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"].rstrip("/")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", DEFAULT_INDEX_NAME)

    credential = DefaultAzureCredential()
    client = SearchIndexClient(
        endpoint=endpoint,
        credential=credential,
        api_version=AZURE_SEARCH_API_VERSION,
    )

    try:
        client.create_or_update_index(
            create_policy_chunk_search_index(index_name),
        )
        deployed = client.get_index(index_name)
    finally:
        client.close()
        credential.close()

    embedding_field = next(field for field in deployed.fields if field.name == "embedding")

    if embedding_field.vector_search_dimensions != EMBEDDING_DIMENSIONS:
        raise RuntimeError("Deployed embedding dimensions do not match the application contract")

    print(
        json.dumps(
            {
                "index": deployed.name,
                "fields": len(deployed.fields),
                "embedding_dimensions": embedding_field.vector_search_dimensions,
                "vector_profile": embedding_field.vector_search_profile_name,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
