"""Production dependency composition selected by VECTOR_BACKEND."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import cast

import psycopg
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from pgvector.psycopg import register_vector
from qdrant_client import QdrantClient

from policy_rag.answering import PolicyAnswerService
from policy_rag.answering.foundry import FoundryAnswerProvider
from policy_rag.config import Settings
from policy_rag.embeddings import FoundryEmbeddingProvider
from policy_rag.indexing.azure_search import AZURE_SEARCH_API_VERSION
from policy_rag.retrieval.azure_ai_search_store import AzureAISearchStore, AzureSearchClient
from policy_rag.retrieval.base import PolicyVectorStore
from policy_rag.retrieval.factory import VectorBackend, create_vector_store
from policy_rag.retrieval.pgvector_store import Connection, PgVectorStore
from policy_rag.retrieval.qdrant_store import QdrantStore

POSTGRES_TOKEN_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"


@dataclass(frozen=True)
class RuntimeComponents:
    service: PolicyAnswerService
    store: PolicyVectorStore
    credential: DefaultAzureCredential

    def close(self) -> None:
        self.store.close()
        self.credential.close()


@contextmanager
def _postgres_connection(
    dsn: str, credential: DefaultAzureCredential | None = None
) -> Iterator[Connection]:
    password = credential.get_token(POSTGRES_TOKEN_SCOPE).token if credential else None
    with psycopg.connect(dsn, password=password) as connection:
        try:
            register_vector(connection)
        except psycopg.ProgrammingError as error:
            if "vector type not found" not in str(error):
                raise
        yield cast(Connection, connection)


def build_runtime(settings: Settings) -> RuntimeComponents:
    credential = DefaultAzureCredential()
    if settings.vector_backend is VectorBackend.AZURE_AI_SEARCH:
        if settings.azure_search_endpoint is None:
            raise ValueError("AZURE_SEARCH_ENDPOINT is required for Azure AI Search")
        client = SearchClient(
            settings.azure_search_endpoint,
            settings.azure_search_index_name,
            credential,
            api_version=AZURE_SEARCH_API_VERSION,
        )
        selected: PolicyVectorStore = AzureAISearchStore(cast(AzureSearchClient, client))
    elif settings.vector_backend is VectorBackend.PGVECTOR:
        postgres_credential = credential if settings.postgres_use_entra else None
        selected = PgVectorStore(
            lambda: _postgres_connection(settings.postgres_dsn, postgres_credential)
        )
    else:
        api_key = settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None
        selected = QdrantStore(
            QdrantClient(
                url=settings.qdrant_url,
                api_key=api_key,
                timeout=settings.qdrant_timeout_seconds,
            ),
            settings.qdrant_collection,
        )
    store = create_vector_store(settings.vector_backend, {settings.vector_backend: selected})
    embeddings = FoundryEmbeddingProvider(
        endpoint=settings.azure_openai_endpoint,
        deployment=settings.azure_openai_embedding_deployment,
        credential=credential,
    )
    answers = FoundryAnswerProvider(
        endpoint=settings.azure_openai_endpoint,
        deployment=settings.azure_openai_chat_deployment,
        credential=credential,
    )
    return RuntimeComponents(PolicyAnswerService(store, embeddings, answers), store, credential)
