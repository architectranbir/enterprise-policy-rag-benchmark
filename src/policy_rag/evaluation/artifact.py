"""Versioned, backend-neutral inputs for a fair vector-only benchmark."""

import gzip
import hashlib
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from policy_rag.embeddings import EmbeddingProvider, EmbeddingVector
from policy_rag.evaluation.models import EvaluationCase, EvaluationDataset
from policy_rag.indexing import IndexedPolicyChunk, policy_chunk_to_indexed_document
from policy_rag.ingestion.chunk_text import policy_chunk_text
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.corpus import load_policy_corpus
from policy_rag.ingestion.sections import extract_policy_sections


class EmbeddedEvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case: EvaluationCase
    query_embedding: EmbeddingVector = Field(min_length=1)


class FairVectorArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    created_at: datetime
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dataset_name: str
    embedding_model: str
    embedding_dimensions: int = Field(gt=0)
    similarity_metric: Literal["cosine"] = "cosine"
    top_k: int = Field(gt=0)
    documents: tuple[IndexedPolicyChunk, ...]
    cases: tuple[EmbeddedEvaluationCase, ...]

    @model_validator(mode="after")
    def validate_fair_inputs(self) -> "FairVectorArtifact":
        document_ids = [document.chunk_id for document in self.documents]
        case_ids = [item.case.case_id for item in self.cases]
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("artifact document chunk IDs must be unique")
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("artifact evaluation case IDs must be unique")
        if any(len(document.embedding) != self.embedding_dimensions for document in self.documents):
            raise ValueError("artifact document embedding dimensions do not match the manifest")
        if any(len(item.query_embedding) != self.embedding_dimensions for item in self.cases):
            raise ValueError("artifact query embedding dimensions do not match the manifest")
        available = set(document_ids)
        if any(
            chunk_id not in available
            for item in self.cases
            for chunk_id in item.case.relevant_chunk_ids
        ):
            raise ValueError("artifact relevance judgments must reference embedded documents")
        return self


def source_digest(corpus_root: Path, dataset_path: Path) -> str:
    """Hash ordered corpus files and the evaluation dataset without machine-specific paths."""

    digest = hashlib.sha256()
    files = sorted(path for path in corpus_root.rglob("*") if path.is_file())
    for path in (*files, dataset_path):
        relative = path.relative_to(corpus_root.parent) if path != dataset_path else Path(path.name)
        digest.update(relative.as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def create_fair_vector_artifact(
    *,
    corpus_root: Path,
    dataset_path: Path,
    provider: EmbeddingProvider,
    batch_size: int = 1,
) -> FairVectorArtifact:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")

    dataset = EvaluationDataset.model_validate_json(dataset_path.read_text(encoding="utf-8"))
    chunks = tuple(
        chunk
        for source in load_policy_corpus(corpus_root)
        for section in extract_policy_sections(source)
        for chunk in create_section_chunks(section)
    )
    texts = tuple(policy_chunk_text(chunk) for chunk in chunks)
    questions = tuple(case.question for case in dataset.cases)
    embeddings = _embed_batches(provider, (*texts, *questions), batch_size)
    document_embeddings = embeddings[: len(chunks)]
    query_embeddings = embeddings[len(chunks) :]

    return FairVectorArtifact(
        created_at=datetime.now(UTC),
        source_sha256=source_digest(corpus_root, dataset_path),
        dataset_name=dataset.name,
        embedding_model=dataset.embedding_model,
        embedding_dimensions=dataset.embedding_dimensions,
        similarity_metric="cosine",
        top_k=dataset.top_k,
        documents=tuple(
            policy_chunk_to_indexed_document(chunk, embedding)
            for chunk, embedding in zip(chunks, document_embeddings, strict=True)
        ),
        cases=tuple(
            EmbeddedEvaluationCase(case=case, query_embedding=embedding)
            for case, embedding in zip(dataset.cases, query_embeddings, strict=True)
        ),
    )


def _embed_batches(
    provider: EmbeddingProvider, texts: Sequence[str], batch_size: int
) -> tuple[EmbeddingVector, ...]:
    return tuple(
        embedding
        for offset in range(0, len(texts), batch_size)
        for embedding in provider.embed(texts[offset : offset + batch_size])
    )


def write_artifact(path: Path, artifact: FairVectorArtifact) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = artifact.model_dump_json(indent=2).encode()
    temporary = path.with_name(f".{path.name}.tmp")
    if path.suffix == ".gz":
        temporary.write_bytes(gzip.compress(payload, mtime=0))
    else:
        temporary.write_bytes(payload)
    temporary.replace(path)


def load_artifact(path: Path) -> FairVectorArtifact:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            payload = stream.read()
    else:
        payload = path.read_text(encoding="utf-8")
    return FairVectorArtifact.model_validate_json(payload)


def artifact_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
