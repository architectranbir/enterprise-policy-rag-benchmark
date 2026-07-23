"""Validate comparable raw runs and produce publish-ready JSON and Markdown summaries."""

import argparse
import csv
import json
from pathlib import Path

from policy_rag.evaluation.results import FairVectorRun

ROOT = Path(__file__).resolve().parents[1]
BACKENDS = ("azure_ai_search", "pgvector", "qdrant")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "benchmark_results" / "raw")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "benchmark_results" / "comparison"
    )
    parser.add_argument(
        "--mode", choices=("fair-vector-only", "platform-optimized"), default="fair-vector-only"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = tuple(
        FairVectorRun.model_validate_json(
            (args.raw_dir / f"{backend}.json").read_text(encoding="utf-8")
        )
        for backend in BACKENDS
    )
    for backend, run in zip(BACKENDS, runs, strict=True):
        raw_path = args.raw_dir / f"{backend}.json"
        with raw_path.with_suffix(".csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(type(run.cases[0]).model_fields))
            writer.writeheader()
            writer.writerows(item.model_dump(mode="json") for item in run.cases)
        raw_path.with_suffix(".md").write_text(
            "\n".join(
                (
                    f"# {run.mode}: {run.backend}",
                    "",
                    f"- Dataset: `{run.dataset_name}`",
                    f"- Cases: {run.case_count}",
                    f"- Measured repetitions: {run.measured_repetitions}",
                    f"- Recall@{run.top_k}: {run.recall_at_k:.4f}",
                    f"- Precision@{run.top_k}: {run.precision_at_k:.4f}",
                    f"- MRR: {run.mean_reciprocal_rank:.4f}",
                    f"- nDCG@{run.top_k}: {run.ndcg_at_k:.4f}",
                    f"- Retrieval p50 / p95: {run.p50_latency_ms:.2f} / {run.p95_latency_ms:.2f} ms",
                    "",
                )
            ),
            encoding="utf-8",
        )
    signatures = {
        (run.artifact_sha256, run.source_sha256, run.dataset_name, run.top_k, run.case_count)
        for run in runs
    }
    if len(signatures) != 1:
        raise ValueError("raw runs are not comparable: artifact or dataset signatures differ")
    if any(run.mode != args.mode for run in runs):
        raise ValueError(f"raw runs do not all belong to the {args.mode} track")

    strong = all(run.measurement_count > 0 for run in runs)
    rows = [
        {
            "backend": run.backend,
            f"recall_at_{run.top_k}": run.recall_at_k,
            "mean_reciprocal_rank": run.mean_reciprocal_rank,
            "mean_latency_ms": run.mean_latency_ms,
            "case_count": run.case_count,
            "created_at": run.created_at.isoformat(),
            **(
                {
                    f"precision_at_{run.top_k}": run.precision_at_k,
                    f"ndcg_at_{run.top_k}": run.ndcg_at_k,
                    "p50_latency_ms": run.p50_latency_ms,
                    "p95_latency_ms": run.p95_latency_ms,
                    "latency_stddev_ms": run.latency_stddev_ms,
                    "measurement_count": run.measurement_count,
                }
                if strong
                else {}
            ),
        }
        for run in runs
    ]
    track_limitation = (
        "Platform-optimised features differ by backend and are intentionally not a controlled "
        "vector-only comparison."
        if args.mode == "platform-optimized"
        else "Platform-optimised hybrid, sparse and semantic features are outside this comparison."
    )
    limitations = (
        "Development-scale results are workload-specific and do not establish a universal winner.",
        "Latency includes one client-side retrieval call but excludes query embedding generation.",
        track_limitation,
        *(
            ()
            if strong
            else (
                "Each backend has one measured run; latency has no warm-up exclusion or confidence interval.",
            )
        ),
    )
    comparison = {
        "mode": args.mode,
        "dataset": runs[0].dataset_name,
        "environment": "development",
        "runs_per_backend": runs[0].measured_repetitions,
        "artifact_sha256": runs[0].artifact_sha256,
        "source_sha256": runs[0].source_sha256,
        "top_k": runs[0].top_k,
        "limitations": limitations,
        "results": rows,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_stem = (
        "fair-vector-comparison" if args.mode == "fair-vector-only" else "platform-comparison"
    )
    (args.output_dir / f"{report_stem}.json").write_text(
        json.dumps(comparison, indent=2) + "\n", encoding="utf-8"
    )

    metric = f"Recall@{runs[0].top_k}"
    lines = [
        (
            "# Fair vector-only retrieval comparison"
            if args.mode == "fair-vector-only"
            else "# Platform-optimised retrieval comparison"
        ),
        "",
        f"Dataset: `{runs[0].dataset_name}` · Cases: {runs[0].case_count} · Top k: {runs[0].top_k}",
        "",
        (
            f"Environment: development · Measured repetitions per backend: {runs[0].measured_repetitions}"
            if strong
            else "Environment: development · Measured runs per backend: 1"
        ),
        "",
        (
            f"| Backend | {metric} | Precision@{runs[0].top_k} | MRR | "
            f"nDCG@{runs[0].top_k} | p50 (ms) | p95 (ms) |"
            if strong
            else f"| Backend | {metric} | MRR | Mean retrieval latency (ms) |"
        ),
        ("|---|---:|---:|---:|---:|---:|---:|" if strong else "|---|---:|---:|---:|"),
        *(
            (
                f"| {run.backend} | {run.recall_at_k:.4f} | {run.precision_at_k:.4f} | "
                f"{run.mean_reciprocal_rank:.4f} | {run.ndcg_at_k:.4f} | "
                f"{run.p50_latency_ms:.2f} | {run.p95_latency_ms:.2f} |"
                if strong
                else f"| {run.backend} | {run.recall_at_k:.4f} | "
                f"{run.mean_reciprocal_rank:.4f} | {run.mean_latency_ms:.2f} |"
            )
            for run in runs
        ),
        "",
        "## Interpretation guardrails",
        "",
        *[f"- {limitation}" for limitation in limitations],
        "",
    ]
    (args.output_dir / f"{report_stem}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote comparison reports to {args.output_dir}")


if __name__ == "__main__":
    main()
