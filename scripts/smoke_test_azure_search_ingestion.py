"""Verify keyless ingestion of one canonical policy chunk into Azure AI Search."""

import json
import os
from pathlib import Path
from typing import Any, cast

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

from policy_rag.embeddings import FoundryEmbeddingProvider
from policy_rag.indexing.azure_ingestion import upload_indexed_policy_chunks
from policy_rag.indexing.document import policy_chunk_to_indexed_document
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.sections import extract_policy_sections
from policy_rag.ingestion.source import load_policy_source

DEFAULT_INDEX_NAME = "policy-chunks-dev-v1"
POLICY_VERSION_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "data" / "synthetic" / "policies" / "POL-HR-001" / "1.0"
)


def main() -> None:
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", DEFAULT_INDEX_NAME)
    credential = DefaultAzureCredential()
    embedding_provider = FoundryEmbeddingProvider(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
        credential=credential,
    )
    search_client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"].rstrip("/"),
        index_name=index_name,
        credential=credential,
    )

    source = load_policy_source(POLICY_VERSION_DIRECTORY)
    section = extract_policy_sections(source)[0]
    chunk = create_section_chunks(section)[0]
    embedding = embedding_provider.embed((chunk.content,))[0]
    document = policy_chunk_to_indexed_document(chunk, embedding)

    try:
        uploaded_keys = upload_indexed_policy_chunks(search_client, (document,))
        deployed = cast(dict[str, Any], search_client.get_document(key=uploaded_keys[0]))
    finally:
        search_client.close()
        credential.close()

    if deployed["chunk_id"] != document.chunk_id:
        raise RuntimeError("Retrieved Azure document does not match the canonical chunk")

    print(
        json.dumps(
            {
                "index": index_name,
                "uploaded_documents": len(uploaded_keys),
                "chunk_id": deployed["chunk_id"],
                "document_id": deployed["document_id"],
                "embedding_dimensions": len(embedding),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
