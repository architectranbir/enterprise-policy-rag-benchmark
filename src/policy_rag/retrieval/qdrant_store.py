"""Qdrant ingestion and filtered cosine retrieval."""

from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models

from policy_rag.indexing import IndexedPolicyChunk
from policy_rag.retrieval.models import PolicyRetrievalRequest, RetrievedPolicyChunk


class QdrantStore:
    def __init__(self, client: QdrantClient, collection_name: str, dimensions: int = 3072) -> None:
        self._client = client
        self._collection_name = collection_name
        self._dimensions = dimensions

    @property
    def backend_name(self) -> str:
        return "qdrant"

    def initialize(self) -> None:
        if not self._client.collection_exists(self._collection_name):
            self._client.create_collection(
                self._collection_name,
                vectors_config=models.VectorParams(
                    size=self._dimensions, distance=models.Distance.COSINE
                ),
            )
        for field_name, field_schema in (
            ("effective_from", models.PayloadSchemaType.DATETIME),
            ("effective_to", models.PayloadSchemaType.DATETIME),
            ("allowed_groups", models.PayloadSchemaType.KEYWORD),
            ("document_id", models.PayloadSchemaType.KEYWORD),
            ("department", models.PayloadSchemaType.KEYWORD),
            ("classification", models.PayloadSchemaType.KEYWORD),
        ):
            self._client.create_payload_index(
                collection_name=self._collection_name,
                field_name=field_name,
                field_schema=field_schema,
                wait=True,
            )

    def upsert(self, documents: tuple[IndexedPolicyChunk, ...]) -> None:
        points = [
            models.PointStruct(
                id=str(uuid5(NAMESPACE_URL, d.chunk_id)),
                vector=list(d.embedding),
                payload={
                    **d.model_dump(mode="json", exclude={"embedding"}),
                    "classification": d.classification.value,
                },
            )
            for d in documents
        ]
        if points:
            self._client.upsert(self._collection_name, points=points, wait=True)

    def retrieve(self, request: PolicyRetrievalRequest) -> tuple[RetrievedPolicyChunk, ...]:
        if request.query_embedding is None:
            raise ValueError("query_embedding is required for vector retrieval")
        if not request.access.user_groups:
            return ()
        must: list[models.Condition] = [
            models.FieldCondition(
                key="effective_from", range=models.DatetimeRange(lte=request.access.as_of)
            ),
            models.FieldCondition(
                key="allowed_groups", match=models.MatchAny(any=list(request.access.user_groups))
            ),
        ]
        for key, value in (
            ("document_id", request.document_id),
            ("department", request.department),
            ("classification", request.classification.value if request.classification else None),
        ):
            if value is not None:
                must.append(models.FieldCondition(key=key, match=models.MatchValue(value=value)))
        response = self._client.query_points(
            self._collection_name,
            query=list(request.query_embedding),
            query_filter=models.Filter(
                must=must,
                should=[
                    models.IsNullCondition(is_null=models.PayloadField(key="effective_to")),
                    models.FieldCondition(
                        key="effective_to", range=models.DatetimeRange(gte=request.access.as_of)
                    ),
                ],
            ),
            limit=request.limit,
            with_payload=True,
        )
        results = []
        for point in response.points:
            payload = dict(point.payload or {})
            payload.pop("allowed_groups", None)
            payload["score"] = point.score
            results.append(RetrievedPolicyChunk.model_validate(payload))
        return tuple(results)

    def ready(self) -> bool:
        try:
            self._client.get_collection(self._collection_name)
            return True
        except Exception:
            return False

    def close(self) -> None:
        self._client.close()
