from datetime import UTC, datetime

import pytest

from policy_rag.evaluation.results import (
    CaseRetrievalResult,
    FairVectorRun,
    decode_run_chunks,
    decode_run_log_lines,
    encode_run_chunks,
)


def run() -> FairVectorRun:
    return FairVectorRun(
        created_at=datetime(2026, 7, 22, tzinfo=UTC),
        backend="qdrant",
        artifact_sha256="a" * 64,
        source_sha256="b" * 64,
        dataset_name="test-fair-vector-v1",
        top_k=5,
        case_count=1,
        recall_at_k=1.0,
        mean_reciprocal_rank=1.0,
        mean_latency_ms=2.5,
        cases=(
            CaseRetrievalResult(
                case_id="EQ-001",
                relevant_chunk_ids=("relevant",),
                retrieved_chunk_ids=("relevant", "other"),
                scores=(0.9, 0.5),
                latency_ms=2.5,
            ),
        ),
    )


def test_log_safe_chunks_round_trip_complete_raw_run() -> None:
    expected = run()
    chunks = encode_run_chunks(expected, chunk_size=40)

    assert len(chunks) > 1
    assert decode_run_chunks(chunks) == expected


def test_rejects_invalid_chunk_size() -> None:
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        encode_run_chunks(run(), chunk_size=0)


def test_decodes_numbered_log_lines() -> None:
    expected = run()
    chunks = encode_run_chunks(expected, chunk_size=40)
    lines = [
        "unrelated summary",
        *(
            f"FAIR_VECTOR_RUN_PART={index}/{len(chunks)}:{chunk}"
            for index, chunk in enumerate(chunks, 1)
        ),
    ]

    assert decode_run_log_lines(lines) == expected


def test_rejects_incomplete_log_lines() -> None:
    chunks = encode_run_chunks(run(), chunk_size=40)

    with pytest.raises(ValueError, match="parts are incomplete"):
        decode_run_log_lines([f"FAIR_VECTOR_RUN_PART=1/{len(chunks)}:{chunks[0]}"])
