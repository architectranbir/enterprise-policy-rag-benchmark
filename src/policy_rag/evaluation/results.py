"""Serializable raw runs and comparisons for fair vector-only evaluation."""

import base64
import gzip
import re
from collections.abc import Iterable
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BackendName = Literal["azure_ai_search", "pgvector", "qdrant"]
RUN_PART_PATTERN = re.compile(r"^FAIR_VECTOR_RUN_PART=(\d+)/(\d+):(.+)$")


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


def encode_run_chunks(run: FairVectorRun, chunk_size: int = 3000) -> tuple[str, ...]:
    """Encode a run into bounded log-safe chunks without losing raw rankings."""

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    compressed = gzip.compress(run.model_dump_json().encode(), mtime=0)
    payload = base64.b64encode(compressed).decode()
    return tuple(
        payload[offset : offset + chunk_size] for offset in range(0, len(payload), chunk_size)
    )


def decode_run_chunks(chunks: tuple[str, ...]) -> FairVectorRun:
    if not chunks:
        raise ValueError("run chunks must not be empty")
    payload = gzip.decompress(base64.b64decode("".join(chunks))).decode()
    return FairVectorRun.model_validate_json(payload)


def decode_run_log_lines(lines: Iterable[str]) -> FairVectorRun:
    """Reassemble one numbered run emitted through bounded console-log records."""

    parts: dict[int, str] = {}
    expected_total: int | None = None
    for line in lines:
        match = RUN_PART_PATTERN.fullmatch(line.strip())
        if match is None:
            continue
        index, total, payload = int(match.group(1)), int(match.group(2)), match.group(3)
        if expected_total is not None and total != expected_total:
            raise ValueError("run log parts disagree on total part count")
        expected_total = total
        if index in parts:
            raise ValueError(f"duplicate run log part {index}")
        parts[index] = payload
    if expected_total is None:
        raise ValueError("no fair-vector run parts found")
    expected_indexes = set(range(1, expected_total + 1))
    if set(parts) != expected_indexes:
        raise ValueError("fair-vector run log parts are incomplete")
    return decode_run_chunks(tuple(parts[index] for index in range(1, expected_total + 1)))
