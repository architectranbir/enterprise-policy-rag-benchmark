"""Run one fair vector-only retrieval benchmark and save complete raw rankings."""

import argparse
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import cast

from policy_rag.config import Settings
from policy_rag.domain.access import PolicyAccessContext
from policy_rag.evaluation.artifact import artifact_digest, load_artifact
from policy_rag.evaluation.results import BackendName, CaseRetrievalResult, FairVectorRun
from policy_rag.retrieval.models import PolicyRetrievalRequest
from policy_rag.runtime import build_runtime

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact",
        type=Path,
        default=ROOT / "data" / "generated" / "fair-vector-v1.json.gz",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--emit-json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings()
    artifact = load_artifact(args.artifact)
    runtime = build_runtime(settings)
    case_results: list[CaseRetrievalResult] = []
    try:
        for embedded in artifact.cases:
            case = embedded.case
            request = PolicyRetrievalRequest(
                access=PolicyAccessContext(
                    user_id=f"benchmark:{case.case_id}",
                    user_groups=case.user_groups,
                    as_of=case.as_of,
                ),
                query_embedding=embedded.query_embedding,
                limit=artifact.top_k,
            )
            started = perf_counter()
            retrieved = runtime.store.retrieve(request)
            latency_ms = (perf_counter() - started) * 1000
            case_results.append(
                CaseRetrievalResult(
                    case_id=case.case_id,
                    relevant_chunk_ids=case.relevant_chunk_ids,
                    retrieved_chunk_ids=tuple(item.chunk_id for item in retrieved),
                    scores=tuple(item.score for item in retrieved),
                    latency_ms=latency_ms,
                )
            )
        backend = runtime.store.backend_name
    finally:
        runtime.close()

    recalls = []
    reciprocal_ranks = []
    for result in case_results:
        relevant = set(result.relevant_chunk_ids)
        recalls.append(len(relevant.intersection(result.retrieved_chunk_ids)) / len(relevant))
        reciprocal_ranks.append(
            next(
                (
                    1 / rank
                    for rank, chunk_id in enumerate(result.retrieved_chunk_ids, 1)
                    if chunk_id in relevant
                ),
                0.0,
            )
        )
    count = len(case_results)
    run = FairVectorRun(
        created_at=datetime.now(UTC),
        backend=cast(BackendName, backend),
        artifact_sha256=artifact_digest(args.artifact),
        source_sha256=artifact.source_sha256,
        dataset_name=artifact.dataset_name,
        top_k=artifact.top_k,
        case_count=count,
        recall_at_k=sum(recalls) / count if count else 0.0,
        mean_reciprocal_rank=sum(reciprocal_ranks) / count if count else 0.0,
        mean_latency_ms=(
            sum(result.latency_ms for result in case_results) / count if count else 0.0
        ),
        cases=tuple(case_results),
    )
    output = args.output or ROOT / "benchmark_results" / "raw" / f"{backend}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(run.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(
        f"{backend}: cases={count} recall@{artifact.top_k}={run.recall_at_k:.4f} "
        f"mrr={run.mean_reciprocal_rank:.4f} mean_latency_ms={run.mean_latency_ms:.2f}"
    )
    if args.emit_json:
        print(f"FAIR_VECTOR_RUN_JSON={run.model_dump_json()}")


if __name__ == "__main__":
    main()
