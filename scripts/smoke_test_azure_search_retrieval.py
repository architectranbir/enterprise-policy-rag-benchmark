"""Verify keyless ACL-safe exact retrieval from Azure AI Search."""

import json
import os
from datetime import date
from typing import cast

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification
from policy_rag.embeddings import FoundryEmbeddingProvider
from policy_rag.indexing.azure_search import AZURE_SEARCH_API_VERSION
from policy_rag.retrieval import PolicyRetrievalRequest
from policy_rag.retrieval.azure_retrieval import (
    AzureSearchQueryClient,
    retrieve_vector_policy_chunks,
)

DEFAULT_INDEX_NAME = "policy-chunks-dev-v1"
DOCUMENT_ID = "POL-HR-001"
AS_OF = date(2026, 7, 20)
QUESTION = "How much may an employee claim for home-office equipment?"


def create_request(
    user_groups: tuple[str, ...],
    query_embedding: tuple[float, ...],
) -> PolicyRetrievalRequest:
    return PolicyRetrievalRequest(
        access=PolicyAccessContext(
            user_id="retrieval-smoke-test",
            user_groups=user_groups,
            as_of=AS_OF,
        ),
        document_id=DOCUMENT_ID,
        classification=PolicyClassification.INTERNAL,
        query_embedding=query_embedding,
        limit=10,
    )


def main() -> None:
    index_name = os.getenv(
        "AZURE_SEARCH_INDEX_NAME",
        DEFAULT_INDEX_NAME,
    )
    credential = DefaultAzureCredential()
    embedding_provider = FoundryEmbeddingProvider(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
        credential=credential,
    )
    search_client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"].rstrip("/"),
        index_name=index_name,
        credential=credential,
        api_version=AZURE_SEARCH_API_VERSION,
    )
    query_client = cast(AzureSearchQueryClient, search_client)

    try:
        query_embedding = embedding_provider.embed((QUESTION,))[0]
        authorized = retrieve_vector_policy_chunks(
            query_client,
            create_request(("employees",), query_embedding),
        )
        denied = retrieve_vector_policy_chunks(
            query_client,
            create_request(("contractors",), query_embedding),
        )
    finally:
        search_client.close()
        credential.close()

    if not authorized:
        raise RuntimeError("Authorized retrieval returned no policy chunks")

    if any(result.document_id != DOCUMENT_ID for result in authorized):
        raise RuntimeError("Authorized retrieval returned an unexpected document")

    if denied:
        raise RuntimeError("Unauthorized group retrieved protected policy chunks")

    print(
        json.dumps(
            {
                "index": index_name,
                "question": QUESTION,
                "query_embedding_dimensions": len(query_embedding),
                "authorized_group": "employees",
                "authorized_results": len(authorized),
                "denied_group": "contractors",
                "denied_results": len(denied),
                "document_id": authorized[0].document_id,
                "chunk_ids": [result.chunk_id for result in authorized],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
