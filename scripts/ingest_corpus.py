"""Ingest the canonical synthetic corpus into the selected VECTOR_BACKEND."""

import os
from pathlib import Path

from azure.identity import DefaultAzureCredential

from policy_rag.config import Settings
from policy_rag.embeddings import FoundryEmbeddingProvider
from policy_rag.indexing import policy_chunk_to_indexed_document
from policy_rag.ingestion.chunk_text import policy_chunk_text
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.corpus import load_policy_corpus
from policy_rag.ingestion.sections import extract_policy_sections
from policy_rag.runtime import build_runtime

CORPUS = Path(__file__).resolve().parents[1] / "data" / "synthetic" / "policies"
DEFAULT_EMBEDDING_BATCH_SIZE = 1


def main() -> None:
    settings = Settings()
    runtime = build_runtime(settings)
    store = runtime.store
    store.initialize()
    chunks = tuple(
        chunk
        for source in load_policy_corpus(CORPUS)
        for section in extract_policy_sections(source)
        for chunk in create_section_chunks(section)
    )
    credential = DefaultAzureCredential()
    provider = FoundryEmbeddingProvider(
        endpoint=settings.azure_openai_endpoint,
        deployment=settings.azure_openai_embedding_deployment,
        credential=credential,
    )
    try:
        batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", str(DEFAULT_EMBEDDING_BATCH_SIZE)))
        if batch_size < 1:
            raise ValueError("EMBEDDING_BATCH_SIZE must be positive")

        embeddings = tuple(
            embedding
            for offset in range(0, len(chunks), batch_size)
            for embedding in provider.embed(
                tuple(policy_chunk_text(chunk) for chunk in chunks[offset : offset + batch_size])
            )
        )
        documents = tuple(
            policy_chunk_to_indexed_document(chunk, embedding)
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        )
        store.upsert(documents)
    finally:
        credential.close()
        runtime.close()
    print(f"Ingested {len(documents)} canonical chunks into {store.backend_name}")


if __name__ == "__main__":
    main()
