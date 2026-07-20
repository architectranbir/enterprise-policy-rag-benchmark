from datetime import date

import pytest
from pydantic import ValidationError

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification
from policy_rag.retrieval import (
    PolicyRetrievalRequest,
    RetrievedPolicyChunk,
)


def create_access() -> PolicyAccessContext:
    return PolicyAccessContext(
        user_id="USER-001",
        user_groups=("employees",),
        as_of=date(2026, 7, 20),
    )


def test_retrieval_request_contains_access_and_exact_filters() -> None:
    request = PolicyRetrievalRequest(
        access=create_access(),
        document_id="POL-HR-001",
        department=" Human Resources ",
        classification=PolicyClassification.INTERNAL,
        limit=5,
    )

    assert request.access.user_groups == ("employees",)
    assert request.document_id == "POL-HR-001"
    assert request.department == "Human Resources"
    assert request.classification is PolicyClassification.INTERNAL
    assert request.limit == 5


def test_retrieval_request_rejects_invalid_limit() -> None:
    with pytest.raises(ValidationError):
        PolicyRetrievalRequest(
            access=create_access(),
            limit=101,
        )


def test_retrieved_chunk_contains_citation_metadata_without_backend_data() -> None:
    result = RetrievedPolicyChunk(
        chunk_id="POL-HR-001:1.0:SEC-006:CHK-001",
        text="Remote Working Policy\nSection 6: Equipment and expenses",
        document_id="POL-HR-001",
        document_title="Remote Working Policy",
        version="1.0",
        effective_from=date(2026, 1, 1),
        effective_to=None,
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        section_id="POL-HR-001:1.0:SEC-006",
        section_number="6",
        section_title="Equipment and expenses",
        section_ordinal=6,
        chunk_ordinal=1,
        score=None,
    )

    payload = result.model_dump()

    assert payload["document_id"] == "POL-HR-001"
    assert payload["section_number"] == "6"
    assert "embedding" not in payload
    assert "allowed_groups" not in payload
