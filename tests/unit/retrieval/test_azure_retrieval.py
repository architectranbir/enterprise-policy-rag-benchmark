from collections.abc import Iterable
from datetime import date
from typing import Any

import pytest

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification
from policy_rag.retrieval import PolicyRetrievalRequest
from policy_rag.retrieval.azure_retrieval import (
    AZURE_RETRIEVAL_FIELDS,
    retrieve_exact_policy_chunks,
)


class FakeSearchClient:
    def __init__(self, results: list[dict[str, Any]]) -> None:
        self.results = results
        self.search_text: str | None = None
        self.filter: str | None = None
        self.select: list[str] | None = None
        self.top: int | None = None

    def search(
        self,
        search_text: str | None = None,
        *,
        filter: str | None = None,
        select: list[str] | None = None,
        top: int | None = None,
    ) -> Iterable[dict[str, Any]]:
        self.search_text = search_text
        self.filter = filter
        self.select = select
        self.top = top
        return self.results


def create_request() -> PolicyRetrievalRequest:
    return PolicyRetrievalRequest(
        access=PolicyAccessContext(
            user_id="USER-001",
            user_groups=("employees",),
            as_of=date(2026, 7, 20),
        ),
        document_id="POL-HR-001",
        limit=5,
    )


def create_azure_result() -> dict[str, Any]:
    return {
        "@search.score": 1.0,
        "chunk_id": "POL-HR-001:1.0:SEC-006:CHK-001",
        "text": ("Remote Working Policy\nSection 6: Equipment and expenses"),
        "document_id": "POL-HR-001",
        "document_title": "Remote Working Policy",
        "version": "1.0",
        "effective_from": "2026-01-01T00:00:00Z",
        "effective_to": None,
        "department": "Human Resources",
        "classification": "internal",
        "section_id": "POL-HR-001:1.0:SEC-006",
        "section_number": "6",
        "section_title": "Equipment and expenses",
        "section_ordinal": 6,
        "chunk_ordinal": 1,
    }


def test_queries_with_secured_filter_and_maps_result() -> None:
    client = FakeSearchClient([create_azure_result()])

    results = retrieve_exact_policy_chunks(client, create_request())

    assert client.search_text == "*"
    assert client.filter is not None
    assert "allowed_groups/any" in client.filter
    assert "effective_from le 2026-07-20T00:00:00Z" in client.filter
    assert client.select == list(AZURE_RETRIEVAL_FIELDS)
    assert "embedding" not in client.select
    assert "allowed_groups" not in client.select
    assert client.top == 5

    assert len(results) == 1
    assert results[0].document_id == "POL-HR-001"
    assert results[0].effective_from == date(2026, 1, 1)
    assert results[0].classification is PolicyClassification.INTERNAL
    assert results[0].score == 1.0


def test_returns_empty_tuple_when_azure_has_no_matches() -> None:
    client = FakeSearchClient([])

    assert retrieve_exact_policy_chunks(client, create_request()) == ()


def test_rejects_invalid_azure_date_value() -> None:
    azure_result = create_azure_result()
    azure_result["effective_from"] = "not-a-date"
    client = FakeSearchClient([azure_result])

    with pytest.raises(
        ValueError,
        match="effective_from must be a date or datetime",
    ):
        retrieve_exact_policy_chunks(client, create_request())
