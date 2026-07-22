"""PostgreSQL/pgvector ingestion and cosine retrieval."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any, Protocol

from pgvector import HalfVector

from policy_rag.indexing import IndexedPolicyChunk
from policy_rag.retrieval.models import PolicyRetrievalRequest, RetrievedPolicyChunk

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS policy_chunks (
  chunk_id text PRIMARY KEY, text text NOT NULL, embedding halfvec({dimensions}) NOT NULL,
  document_id text NOT NULL, document_title text NOT NULL, version text NOT NULL,
  effective_from date NOT NULL, effective_to date, department text NOT NULL,
  classification text NOT NULL, allowed_groups text[] NOT NULL,
  section_id text NOT NULL, section_number text NOT NULL, section_title text NOT NULL,
  section_ordinal integer NOT NULL, chunk_ordinal integer NOT NULL
);
CREATE INDEX IF NOT EXISTS policy_chunks_embedding_hnsw
ON policy_chunks USING hnsw (embedding halfvec_cosine_ops);
"""


class Cursor(Protocol):
    def execute(self, query: str, params: Any = None) -> Any: ...
    def executemany(self, query: str, params_seq: Any) -> Any: ...
    def fetchall(self) -> list[tuple[Any, ...]]: ...


class Connection(Protocol):
    def cursor(self) -> AbstractContextManager[Cursor]: ...
    def commit(self) -> None: ...


class PgVectorStore:
    def __init__(
        self,
        connection_factory: Callable[[], AbstractContextManager[Connection]],
        dimensions: int = 3072,
    ) -> None:
        if dimensions < 1 or dimensions > 4000:
            raise ValueError("dimensions must be between 1 and 4000 for halfvec HNSW")
        self._connection_factory = connection_factory
        self._dimensions = dimensions

    @property
    def backend_name(self) -> str:
        return "pgvector"

    def initialize(self) -> None:
        with self._connection_factory() as connection, connection.cursor() as cursor:
            cursor.execute(SCHEMA_SQL.format(dimensions=self._dimensions))
            connection.commit()

    def upsert(self, documents: tuple[IndexedPolicyChunk, ...]) -> None:
        if not documents:
            return
        query = """INSERT INTO policy_chunks VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (chunk_id) DO UPDATE SET text=EXCLUDED.text, embedding=EXCLUDED.embedding,
        document_title=EXCLUDED.document_title, effective_from=EXCLUDED.effective_from,
        effective_to=EXCLUDED.effective_to, department=EXCLUDED.department,
        classification=EXCLUDED.classification, allowed_groups=EXCLUDED.allowed_groups,
        section_title=EXCLUDED.section_title"""
        values = [
            (
                d.chunk_id,
                d.text,
                HalfVector(list(d.embedding)),
                d.document_id,
                d.document_title,
                d.version,
                d.effective_from,
                d.effective_to,
                d.department,
                d.classification.value,
                list(d.allowed_groups),
                d.section_id,
                d.section_number,
                d.section_title,
                d.section_ordinal,
                d.chunk_ordinal,
            )
            for d in documents
        ]
        with self._connection_factory() as connection, connection.cursor() as cursor:
            cursor.executemany(query, values)
            connection.commit()

    def retrieve(self, request: PolicyRetrievalRequest) -> tuple[RetrievedPolicyChunk, ...]:
        if request.query_embedding is None:
            raise ValueError("query_embedding is required for vector retrieval")
        if not request.access.user_groups:
            return ()
        clauses = [
            "effective_from <= %s",
            "(effective_to IS NULL OR effective_to >= %s)",
            "allowed_groups && %s",
        ]
        query_vector = HalfVector(list(request.query_embedding))
        params: list[Any] = [
            query_vector,
            request.access.as_of,
            request.access.as_of,
            list(request.access.user_groups),
        ]
        for column, value in (
            ("document_id", request.document_id),
            ("department", request.department),
            ("classification", request.classification.value if request.classification else None),
        ):
            if value is not None:
                clauses.append(f"{column} = %s")
                params.append(value)
        params.extend([query_vector, request.limit])
        query = f"""SELECT chunk_id,text,document_id,document_title,version,effective_from,
        effective_to,department,classification,section_id,section_number,section_title,
        section_ordinal,chunk_ordinal,1-(embedding <=> %s) AS score FROM policy_chunks
        WHERE {" AND ".join(clauses)} ORDER BY embedding <=> %s LIMIT %s"""
        with self._connection_factory() as connection, connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        return tuple(
            RetrievedPolicyChunk(
                chunk_id=r[0],
                text=r[1],
                document_id=r[2],
                document_title=r[3],
                version=r[4],
                effective_from=r[5],
                effective_to=r[6],
                department=r[7],
                classification=r[8],
                section_id=r[9],
                section_number=r[10],
                section_title=r[11],
                section_ordinal=r[12],
                chunk_ordinal=r[13],
                score=float(r[14]),
            )
            for r in rows
        )

    def ready(self) -> bool:
        try:
            with self._connection_factory() as connection, connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Connections are scoped per operation and require no store-level cleanup."""
