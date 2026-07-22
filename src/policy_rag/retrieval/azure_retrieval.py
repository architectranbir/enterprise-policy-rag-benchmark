"""Retrieve secured policy chunks from Azure AI Search."""

from collections.abc import Iterable
from datetime import date, datetime
from typing import Any, Protocol

from azure.search.documents.models import VectorizedQuery

from policy_rag.indexing.azure_search import EMBEDDING_DIMENSIONS, SEMANTIC_CONFIGURATION_NAME
from policy_rag.retrieval.azure_filter import build_azure_exact_filter
from policy_rag.retrieval.models import (
    PolicyRetrievalRequest,
    RetrievedPolicyChunk,
)

AZURE_RETRIEVAL_FIELDS = (
    "chunk_id",
    "text",
    "document_id",
    "document_title",
    "version",
    "effective_from",
    "effective_to",
    "department",
    "classification",
    "section_id",
    "section_number",
    "section_title",
    "section_ordinal",
    "chunk_ordinal",
)


class AzureSearchQueryClient(Protocol):
    """Small Azure client contract required for exact retrieval."""

    def search(
        self,
        search_text: str | None = None,
        *,
        filter: str | None = None,
        select: list[str] | None = None,
        top: int | None = None,
        vector_queries: list[VectorizedQuery] | None = None,
        query_type: str | None = None,
        semantic_configuration_name: str | None = None,
    ) -> Iterable[dict[str, Any]]:
        """Search indexed documents."""


def _date_value(value: Any, field_name: str) -> date:
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError as error:
            raise ValueError(f"{field_name} must be a date or datetime") from error

    raise ValueError(f"{field_name} must be a date or datetime")


def _optional_date_value(value: Any, field_name: str) -> date | None:
    if value is None:
        return None

    return _date_value(value, field_name)


def _map_azure_result(result: dict[str, Any]) -> RetrievedPolicyChunk:
    score_value = result.get("@search.score")

    return RetrievedPolicyChunk(
        chunk_id=result["chunk_id"],
        text=result["text"],
        document_id=result["document_id"],
        document_title=result["document_title"],
        version=result["version"],
        effective_from=_date_value(
            result["effective_from"],
            "effective_from",
        ),
        effective_to=_optional_date_value(
            result.get("effective_to"),
            "effective_to",
        ),
        department=result["department"],
        classification=result["classification"],
        section_id=result["section_id"],
        section_number=result["section_number"],
        section_title=result["section_title"],
        section_ordinal=result["section_ordinal"],
        chunk_ordinal=result["chunk_ordinal"],
        score=float(score_value) if score_value is not None else None,
    )


def retrieve_exact_policy_chunks(
    client: AzureSearchQueryClient,
    request: PolicyRetrievalRequest,
) -> tuple[RetrievedPolicyChunk, ...]:
    """Retrieve ACL-safe exact metadata matches from Azure AI Search."""

    results = client.search(
        search_text="*",
        filter=build_azure_exact_filter(request),
        select=list(AZURE_RETRIEVAL_FIELDS),
        top=request.limit,
    )

    return tuple(_map_azure_result(result) for result in results)


def retrieve_vector_policy_chunks(
    client: AzureSearchQueryClient,
    request: PolicyRetrievalRequest,
) -> tuple[RetrievedPolicyChunk, ...]:
    """Retrieve nearest chunks while enforcing effective-date and ACL filters."""

    if request.query_embedding is None:
        raise ValueError("query_embedding is required for vector retrieval")
    if len(request.query_embedding) != EMBEDDING_DIMENSIONS:
        raise ValueError(f"query_embedding must contain {EMBEDDING_DIMENSIONS} values")

    vector_query = VectorizedQuery(
        vector=list(request.query_embedding),
        fields="embedding",
        k_nearest_neighbors=request.limit,
        exhaustive=False,
    )
    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        filter=build_azure_exact_filter(request),
        select=list(AZURE_RETRIEVAL_FIELDS),
        top=request.limit,
    )

    return tuple(_map_azure_result(result) for result in results)


def retrieve_optimized_policy_chunks(
    client: AzureSearchQueryClient,
    request: PolicyRetrievalRequest,
) -> tuple[RetrievedPolicyChunk, ...]:
    """Use Azure hybrid fusion and semantic ranking; never used by fair mode."""

    if request.query_embedding is None or request.query_text is None:
        raise ValueError("query_embedding and query_text are required for optimized retrieval")
    vector_query = VectorizedQuery(
        vector=list(request.query_embedding),
        fields="embedding",
        k_nearest_neighbors=max(request.limit, 50),
        exhaustive=False,
    )
    results = client.search(
        search_text=request.query_text,
        vector_queries=[vector_query],
        query_type="semantic",
        semantic_configuration_name=SEMANTIC_CONFIGURATION_NAME,
        filter=build_azure_exact_filter(request),
        select=list(AZURE_RETRIEVAL_FIELDS),
        top=request.limit,
    )
    return tuple(_map_azure_result(result) for result in results)
