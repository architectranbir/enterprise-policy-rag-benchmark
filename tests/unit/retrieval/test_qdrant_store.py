from datetime import date

from qdrant_client import QdrantClient

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification
from policy_rag.indexing import IndexedPolicyChunk
from policy_rag.retrieval.models import PolicyRetrievalRequest, RetrievalMode
from policy_rag.retrieval.qdrant_store import QdrantStore


def document() -> IndexedPolicyChunk:
    return IndexedPolicyChunk(
        chunk_id="POL-HR-001:1.0:SEC-006:CHK-001",
        text="GBP 250",
        embedding=(1.0, 0.0, 0.0),
        document_id="POL-HR-001",
        document_title="Remote Working",
        version="1.0",
        effective_from=date(2026, 1, 1),
        effective_to=None,
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees",),
        section_id="POL-HR-001:1.0:SEC-006",
        section_number="6",
        section_title="Equipment",
        section_ordinal=6,
        chunk_ordinal=1,
    )


def request(groups: tuple[str, ...]) -> PolicyRetrievalRequest:
    return PolicyRetrievalRequest(
        access=PolicyAccessContext(user_id="u", user_groups=groups, as_of=date(2026, 7, 1)),
        query_embedding=(1.0, 0.0, 0.0),
        limit=5,
    )


def test_qdrant_round_trip_enforces_acl() -> None:
    store = QdrantStore(QdrantClient(":memory:"), "chunks", dimensions=3)
    store.initialize()
    store.upsert((document(),))
    assert store.retrieve(request(("employees",)))[0].chunk_id == document().chunk_id
    assert store.retrieve(request(("contractors",))) == ()


def test_qdrant_optimized_dense_sparse_round_trip_is_separate() -> None:
    store = QdrantStore(QdrantClient(":memory:"), "optimized", dimensions=3, optimized_schema=True)
    store.initialize()
    store.upsert((document(),))
    optimized = request(("employees",)).model_copy(
        update={"mode": RetrievalMode.PLATFORM_OPTIMIZED, "query_text": "GBP 250"}
    )
    assert store.retrieve(optimized)[0].chunk_id == document().chunk_id
