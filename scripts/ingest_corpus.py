"""Ingest the canonical synthetic corpus into the selected VECTOR_BACKEND."""

from pathlib import Path

from azure.identity import DefaultAzureCredential

from policy_rag.config import Settings
from policy_rag.embeddings import FoundryEmbeddingProvider
from policy_rag.indexing import embed_policy_chunk
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.corpus import load_policy_corpus
from policy_rag.ingestion.sections import extract_policy_sections
from policy_rag.runtime import build_runtime

CORPUS = Path(__file__).resolve().parents[1] / "data" / "synthetic" / "policies"


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
        documents = tuple(embed_policy_chunk(chunk, provider) for chunk in chunks)
        store.upsert(documents)
    finally:
        credential.close()
        runtime.close()
    print(f"Ingested {len(documents)} canonical chunks into {store.backend_name}")


if __name__ == "__main__":
    main()
