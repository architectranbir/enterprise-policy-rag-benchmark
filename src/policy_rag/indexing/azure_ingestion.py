"""Upload backend-neutral policy chunks to Azure AI Search."""

from collections.abc import Sequence
from typing import Any, Protocol, cast

from azure.search.documents.models import IndexingResult

from policy_rag.indexing.azure_document import indexed_chunk_to_azure_document
from policy_rag.indexing.document import IndexedPolicyChunk


class AzureSearchUploadClient(Protocol):
    """Small client contract required for Azure document ingestion."""

    def upload_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> list[IndexingResult]:
        """Upload one batch of documents."""


class AzureSearchUploadError(RuntimeError):
    """Raised when Azure rejects any document in an upload batch."""


def upload_indexed_policy_chunks(
    client: AzureSearchUploadClient,
    documents: Sequence[IndexedPolicyChunk],
) -> tuple[str, ...]:
    """Upload a batch and return the successfully indexed Azure keys."""

    if not documents:
        return ()

    payloads = [
        cast(
            dict[str, Any],
            indexed_chunk_to_azure_document(document),
        )
        for document in documents
    ]

    results = client.upload_documents(documents=payloads)

    if len(results) != len(payloads):
        raise AzureSearchUploadError(
            f"Azure returned {len(results)} results for {len(payloads)} documents"
        )

    failures = [result for result in results if not result.succeeded]
    if failures:
        details = "; ".join(
            f"{result.key}: {result.error_message or 'unknown indexing error'}"
            for result in failures
        )
        raise AzureSearchUploadError(f"Azure document upload failed: {details}")

    return tuple(result.key for result in results)
