"""Run one fair vector-only retrieval benchmark and save complete raw rankings."""

import argparse
import csv
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import cast

from policy_rag.config import Settings
from policy_rag.domain.access import PolicyAccessContext
from policy_rag.evaluation.artifact import EmbeddedEvaluationCase, artifact_digest, load_artifact
from policy_rag.evaluation.results import (
    BackendName,
    CaseRetrievalResult,
    FairVectorRun,
    encode_run_chunks,
    latency_summary,
)
from policy_rag.evaluation.runner import retrieval_metrics
from policy_rag.retrieval.models import PolicyRetrievalRequest, RetrievalMode
from policy_rag.runtime import build_runtime

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    emit_json_default = os.getenv("BENCHMARK_EMIT_JSON", "false").lower() in {
        "1",
        "true",
        "yes",
    }
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact",
        type=Path,
        default=ROOT / "data" / "generated" / "fair-vector-v1.json.gz",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--emit-json", action="store_true", default=emit_json_default)
    parser.add_argument(
        "--warmup-requests", type=int, default=int(os.getenv("BENCHMARK_WARMUP_REQUESTS", "3"))
    )
    parser.add_argument(
        "--repetitions", type=int, default=int(os.getenv("BENCHMARK_REPETITIONS", "5"))
    )
    parser.add_argument("--csv-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument(
        "--mode",
        choices=("fair-vector-only", "platform-optimized"),
        default=os.getenv("BENCHMARK_MODE", "fair-vector-only"),
    )
    return parser.parse_args([argument for argument in sys.argv[1:] if argument])


def main() -> None:
    args = parse_args()
    settings = Settings()
    artifact = load_artifact(args.artifact)
    runtime = build_runtime(settings)
    case_results: list[CaseRetrievalResult] = []
    try:
        if args.warmup_requests < 0 or args.repetitions < 1:
            raise ValueError("warmup requests must be non-negative and repetitions positive")

        def request_for(item: EmbeddedEvaluationCase) -> PolicyRetrievalRequest:
            return PolicyRetrievalRequest(
                access=PolicyAccessContext(
                    user_id=f"benchmark:{item.case.case_id}",
                    user_groups=item.case.user_groups,
                    as_of=item.case.as_of,
                ),
                query_embedding=item.query_embedding,
                query_text=(item.case.question if args.mode == "platform-optimized" else None),
                mode=(
                    RetrievalMode.PLATFORM_OPTIMIZED
                    if args.mode == "platform-optimized"
                    else RetrievalMode.FAIR_VECTOR
                ),
                limit=artifact.top_k,
            )

        for index in range(args.warmup_requests):
            runtime.store.retrieve(request_for(artifact.cases[index % len(artifact.cases)]))
        for repetition in range(1, args.repetitions + 1):
            for embedded in artifact.cases:
                case = embedded.case
                started = perf_counter()
                retrieved = runtime.store.retrieve(request_for(embedded))
                latency_ms = (perf_counter() - started) * 1000
                retrieved_ids = tuple(item.chunk_id for item in retrieved)
                recall, precision, reciprocal_rank, ndcg = retrieval_metrics(
                    case.relevant_chunk_ids, retrieved_ids
                )
                case_results.append(
                    CaseRetrievalResult(
                        case_id=case.case_id,
                        relevant_chunk_ids=case.relevant_chunk_ids,
                        retrieved_chunk_ids=retrieved_ids,
                        scores=tuple(item.score for item in retrieved),
                        latency_ms=latency_ms,
                        repetition=repetition,
                        recall_at_k=recall,
                        precision_at_k=precision,
                        reciprocal_rank=reciprocal_rank,
                        ndcg_at_k=ndcg,
                    )
                )
        backend = runtime.store.backend_name
    finally:
        runtime.close()

    recalls = [result.recall_at_k for result in case_results]
    precisions = [result.precision_at_k for result in case_results]
    reciprocal_ranks = [result.reciprocal_rank for result in case_results]
    ndcgs = [result.ndcg_at_k for result in case_results]
    count = len(case_results)
    latencies = latency_summary(tuple(result.latency_ms for result in case_results))
    run = FairVectorRun(
        created_at=datetime.now(UTC),
        mode=args.mode,
        backend=cast(BackendName, backend),
        artifact_sha256=artifact_digest(args.artifact),
        source_sha256=artifact.source_sha256,
        dataset_name=artifact.dataset_name,
        top_k=artifact.top_k,
        case_count=len(artifact.cases),
        measurement_count=count,
        recall_at_k=sum(recalls) / count if count else 0.0,
        mean_reciprocal_rank=sum(reciprocal_ranks) / count if count else 0.0,
        mean_latency_ms=(
            sum(result.latency_ms for result in case_results) / count if count else 0.0
        ),
        precision_at_k=sum(precisions) / count if count else 0.0,
        ndcg_at_k=sum(ndcgs) / count if count else 0.0,
        warmup_requests=args.warmup_requests,
        measured_repetitions=args.repetitions,
        median_latency_ms=latencies["median"],
        p50_latency_ms=latencies["p50"],
        p95_latency_ms=latencies["p95"],
        latency_stddev_ms=latencies["stddev"],
        cases=tuple(case_results),
    )
    output = args.output
    if output is None and not args.emit_json:
        track = "raw" if args.mode == "fair-vector-only" else "platform-optimized/raw"
        output = ROOT / "benchmark_results" / track / f"{backend}.json"
    if output is not None:
        if args.csv_output is None:
            args.csv_output = output.with_suffix(".csv")
        if args.markdown_output is None:
            args.markdown_output = output.with_suffix(".md")
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(run.model_dump_json(indent=2) + "\n", encoding="utf-8")
    if args.csv_output is not None:
        args.csv_output.parent.mkdir(parents=True, exist_ok=True)
        with args.csv_output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(case_results[0].model_fields))
            writer.writeheader()
            writer.writerows(item.model_dump(mode="json") for item in case_results)
    if args.markdown_output is not None:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(
            "\n".join(
                (
                    f"# {args.mode} benchmark: {backend}",
                    "",
                    f"- Dataset: `{artifact.dataset_name}`",
                    f"- Warm-ups: {args.warmup_requests}",
                    f"- Measured repetitions: {args.repetitions}",
                    f"- Recall@{artifact.top_k}: {run.recall_at_k:.4f}",
                    f"- Precision@{artifact.top_k}: {run.precision_at_k:.4f}",
                    f"- MRR: {run.mean_reciprocal_rank:.4f}",
                    f"- nDCG@{artifact.top_k}: {run.ndcg_at_k:.4f}",
                    f"- Retrieval p50 / p95: {run.p50_latency_ms:.2f} / {run.p95_latency_ms:.2f} ms",
                    "",
                    (
                        "Query embeddings are precomputed; generation is intentionally excluded "
                        "from this retrieval benchmark."
                    ),
                    "",
                )
            ),
            encoding="utf-8",
        )
    print(
        f"{backend}: cases={run.case_count} measurements={count} "
        f"recall@{artifact.top_k}={run.recall_at_k:.4f} "
        f"mrr={run.mean_reciprocal_rank:.4f} mean_latency_ms={run.mean_latency_ms:.2f}"
    )
    if args.emit_json:
        chunks = encode_run_chunks(run)
        for index, chunk in enumerate(chunks, 1):
            print(f"FAIR_VECTOR_RUN_PART={index}/{len(chunks)}:{chunk}")


if __name__ == "__main__":
    main()
