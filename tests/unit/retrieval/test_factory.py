from typing import cast

import pytest

from policy_rag.retrieval.base import PolicyVectorStore
from policy_rag.retrieval.factory import VectorBackend, create_vector_store


def test_factory_returns_only_selected_backend() -> None:
    selected = cast(PolicyVectorStore, object())
    assert create_vector_store(VectorBackend.QDRANT, {VectorBackend.QDRANT: selected}) is selected


def test_factory_rejects_unconfigured_backend() -> None:
    with pytest.raises(ValueError, match="not configured"):
        create_vector_store(VectorBackend.PGVECTOR, {})
