from datetime import date
from typing import Any

import pytest
from azure.search.documents.models import IndexingResult

from policy_rag.domain.policy import PolicyClassification
from policy_rag.indexing.azure_document import azure_document_key
from policy_rag.indexing.azure_ingestion import (
    AzureSearchUploadError,
    upload_indexed_policy_chunks,
)
from policy_rag.indexing.document import IndexedPolicyChunk


class FakeSearchClient:
    def __init__(self, results: list[IndexingResult]) -> None:
        self.results = results
        self.uploaded: list[dict[str, Any]] | None = None

    def upload_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> list[IndexingResult]:
        self.uploaded = documents
        return self.results


def create_document() -> IndexedPolicyChunk:
    return IndexedPolicyChunk(
        chunk_id="POL-HR-001:1.0:SEC-006:CHK-001",
        text="Remote Working Policy\nSection 6: Equipment and expenses",
        embedding=tuple(0.0 for _ in range(3072)),
        document_id="POL-HR-001",
        document_title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        effective_to=None,
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees", "human-resources"),
        section_id="POL-HR-001:1.0:SEC-006",
        section_number="6",
        section_title="Equipment and expenses",
        section_ordinal=6,
        chunk_ordinal=1,
    )


def test_uploads_mapped_documents_and_returns_azure_keys() -> None:
    document = create_document()
    key = azure_document_key(document.chunk_id)
    client = FakeSearchClient(
        [
            IndexingResult(
                key=key,
                succeeded=True,
                status_code=201,
                error_message=None,
            )
        ]
    )

    uploaded_keys = upload_indexed_policy_chunks(client, [document])

    assert uploaded_keys == (key,)
    assert client.uploaded is not None
    assert client.uploaded[0]["id"] == key
    assert client.uploaded[0]["chunk_id"] == document.chunk_id
    assert len(client.uploaded[0]["embedding"]) == 3072


def test_rejects_partial_document_failure() -> None:
    document = create_document()
    key = azure_document_key(document.chunk_id)
    client = FakeSearchClient(
        [
            IndexingResult(
                key=key,
                succeeded=False,
                status_code=400,
                error_message="Invalid document",
            )
        ]
    )

    with pytest.raises(
        AzureSearchUploadError,
        match="Invalid document",
    ):
        upload_indexed_policy_chunks(client, [document])


def test_rejects_missing_indexing_results() -> None:
    client = FakeSearchClient([])

    with pytest.raises(
        AzureSearchUploadError,
        match="returned 0 results for 1 documents",
    ):
        upload_indexed_policy_chunks(client, [create_document()])


def test_empty_batch_does_not_call_azure() -> None:
    client = FakeSearchClient([])

    assert upload_indexed_policy_chunks(client, []) == ()
    assert client.uploaded is None
