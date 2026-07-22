"""Serializable raw runs and comparisons for fair vector-only evaluation."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BackendName = Literal["azure_ai_search", "pgvector", "qdrant"]


class CaseRetrievalResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    relevant_chunk_ids: tuple[str, ...]
    retrieved_chunk_ids: tuple[str, ...]
    scores: tuple[float | None, ...]
    latency_ms: float = Field(ge=0)


class FairVectorRun(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    created_at: datetime
    backend: BackendName
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dataset_name: str
    top_k: int = Field(gt=0)
    case_count: int = Field(ge=0)
    recall_at_k: float = Field(ge=0, le=1)
    mean_reciprocal_rank: float = Field(ge=0, le=1)
    mean_latency_ms: float = Field(ge=0)
    cases: tuple[CaseRetrievalResult, ...]
