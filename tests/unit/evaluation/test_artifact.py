from collections.abc import Sequence
from datetime import date
from pathlib import Path

import pytest

from policy_rag.embeddings import EmbeddingVector
from policy_rag.evaluation.artifact import (
    create_fair_vector_artifact,
    load_artifact,
    write_artifact,
)


class DeterministicEmbeddingProvider:
    def __init__(self, dimensions: int = 3) -> None:
        self.dimensions = dimensions
        self.texts: list[str] = []

    def embed(self, texts: Sequence[str], /) -> tuple[EmbeddingVector, ...]:
        self.texts.extend(texts)
        return tuple(
            tuple(float(index + offset) for offset in range(self.dimensions))
            for index, _ in enumerate(texts)
        )


def write_policy(root: Path) -> None:
    version = root / "POL-TEST-001" / "1.0"
    version.mkdir(parents=True)
    (version / "metadata.json").write_text(
        """{
  "document_id": "POL-TEST-001",
  "title": "Test Policy",
  "version": "1.0",
  "effective_from": "2026-01-01",
  "effective_to": null,
  "department": "Testing",
  "classification": "internal",
  "allowed_groups": ["employees"]
}
""",
        encoding="utf-8",
    )
    (version / "content.md").write_text(
        "# Test Policy\n\n## 1. Purpose\n\nEmployees must test deterministic artifacts.\n",
        encoding="utf-8",
    )


def write_dataset(path: Path, dimensions: int = 3) -> None:
    path.write_text(
        f"""{{
  "name": "test-fair-vector-v1",
  "mode": "fair-vector-only",
  "embedding_model": "test-embedding",
  "embedding_dimensions": {dimensions},
  "similarity_metric": "cosine",
  "top_k": 5,
  "cases": [{{
    "case_id": "EQ-001",
    "question": "What must employees test?",
    "user_groups": ["employees"],
    "as_of": "2026-07-22",
    "relevant_chunk_ids": ["POL-TEST-001:1.0:SEC-001:CHK-001"]
  }}]
}}
""",
        encoding="utf-8",
    )


def test_creates_and_round_trips_one_shared_embedding_artifact(tmp_path: Path) -> None:
    corpus = tmp_path / "policies"
    dataset = tmp_path / "dataset.json"
    write_policy(corpus)
    write_dataset(dataset)
    provider = DeterministicEmbeddingProvider()

    artifact = create_fair_vector_artifact(
        corpus_root=corpus,
        dataset_path=dataset,
        provider=provider,
        batch_size=2,
    )
    output = tmp_path / "artifact.json.gz"
    write_artifact(output, artifact)

    assert load_artifact(output) == artifact
    assert len(artifact.documents) == 1
    assert len(artifact.cases) == 1
    assert len(provider.texts) == 2
    assert artifact.cases[0].case.as_of == date(2026, 7, 22)


def test_rejects_invalid_batch_size(tmp_path: Path) -> None:
    corpus = tmp_path / "policies"
    dataset = tmp_path / "dataset.json"
    write_policy(corpus)
    write_dataset(dataset)

    with pytest.raises(ValueError, match="batch_size must be positive"):
        create_fair_vector_artifact(
            corpus_root=corpus,
            dataset_path=dataset,
            provider=DeterministicEmbeddingProvider(),
            batch_size=0,
        )
