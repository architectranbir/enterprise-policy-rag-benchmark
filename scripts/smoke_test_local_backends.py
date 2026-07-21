"""Run a synthetic ACL round trip against local PostgreSQL and Qdrant."""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from typing import cast

import psycopg
from pgvector.psycopg import register_vector
from qdrant_client import QdrantClient

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification
from policy_rag.indexing import IndexedPolicyChunk
from policy_rag.retrieval.models import PolicyRetrievalRequest
from policy_rag.retrieval.pgvector_store import Connection, PgVectorStore
from policy_rag.retrieval.qdrant_store import QdrantStore


@contextmanager
def postgres_connection() -> Iterator[Connection]:
    dsn = os.environ["LOCAL_POSTGRES_DSN"]
    with psycopg.connect(dsn) as connection:
        try:
            register_vector(connection)
        except psycopg.ProgrammingError as error:
            if "vector type not found" not in str(error):
                raise
        yield cast(Connection, connection)


def request(groups: tuple[str, ...]) -> PolicyRetrievalRequest:
    return PolicyRetrievalRequest(
        access=PolicyAccessContext(
            user_id="integration-test",
            user_groups=groups,
            as_of=date(2026, 7, 22),
        ),
        query_embedding=(1.0, 0.0, 0.0),
        limit=5,
    )


def main() -> None:
    document = IndexedPolicyChunk(
        chunk_id="SYN-LIVE:1:SEC-001:CHK-001",
        text="Synthetic live integration evidence.",
        embedding=(1.0, 0.0, 0.0),
        document_id="SYN-LIVE",
        document_title="Synthetic Live Integration Policy",
        version="1",
        effective_from=date(2026, 1, 1),
        effective_to=None,
        department="Engineering",
        classification=PolicyClassification.INTERNAL,
        allowed_groups=("employees",),
        section_id="SYN-LIVE:1:SEC-001",
        section_number="1",
        section_title="Synthetic Test",
        section_ordinal=1,
        chunk_ordinal=1,
    )

    postgres = PgVectorStore(postgres_connection, dimensions=3)
    postgres.initialize()
    postgres.upsert((document,))
    assert postgres.retrieve(request(("employees",)))[0].chunk_id == document.chunk_id
    assert postgres.retrieve(request(("contractors",))) == ()

    qdrant = QdrantStore(
        QdrantClient(
            url=os.environ.get("LOCAL_QDRANT_URL", "http://localhost:6333"),
            api_key=os.environ["LOCAL_QDRANT_API_KEY"],
        ),
        "integration_chunks",
        dimensions=3,
    )
    try:
        qdrant.initialize()
        qdrant.upsert((document,))
        assert qdrant.retrieve(request(("employees",)))[0].chunk_id == document.chunk_id
        assert qdrant.retrieve(request(("contractors",))) == ()
    finally:
        qdrant.close()

    print("PostgreSQL/pgvector and Qdrant live ACL integration passed.")


if __name__ == "__main__":
    main()
