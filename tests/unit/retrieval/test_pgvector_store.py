from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from typing import Any

from policy_rag.domain.access import PolicyAccessContext
from policy_rag.retrieval.models import PolicyRetrievalRequest, RetrievalMode
from policy_rag.retrieval.pgvector_store import Connection, PgVectorStore


class Cursor:
    query = ""
    params: list[Any] = []

    def __enter__(self) -> "Cursor":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def execute(self, query: str, params: Any = None) -> None:
        self.query = query
        self.params = params

    def executemany(self, query: str, params_seq: Any) -> None:
        pass

    def fetchall(self) -> list[tuple[Any, ...]]:
        return []


class FakeConnection:
    def __init__(self, cursor: Cursor) -> None:
        self._cursor = cursor

    def cursor(self) -> Cursor:
        return self._cursor

    def commit(self) -> None:
        pass


def test_pgvector_optimized_parameter_order_matches_fts_and_vector_sql() -> None:
    cursor = Cursor()

    @contextmanager
    def connection() -> Iterator[Connection]:
        yield FakeConnection(cursor)

    store = PgVectorStore(connection, dimensions=3)
    store.retrieve(
        PolicyRetrievalRequest(
            access=PolicyAccessContext(
                user_id="u", user_groups=("employees",), as_of=date(2026, 7, 22)
            ),
            query_embedding=(1.0, 0.0, 0.0),
            query_text="home office",
            mode=RetrievalMode.PLATFORM_OPTIMIZED,
            limit=5,
        )
    )
    assert "websearch_to_tsquery" in cursor.query
    assert cursor.params[0] == "home office"
    assert cursor.params[2:5] == [date(2026, 7, 22), date(2026, 7, 22), ["employees"]]
    assert cursor.params[-1] == 5
