"""Create a publish-ready comparison for enterprise-control or end-to-end runs."""

import argparse
import json
from pathlib import Path
from typing import Any

from policy_rag.evaluation.enterprise import EnterpriseEvaluationResult
from policy_rag.evaluation.results import latency_summary

BACKENDS = ("azure_ai_search", "pgvector", "qdrant")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--title", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = tuple(
        EnterpriseEvaluationResult.model_validate_json(
            (args.input_dir / f"{backend}.json").read_text(encoding="utf-8")
        )
        for backend in BACKENDS
    )
    if len({result.dataset_name for result in results}) != 1:
        raise ValueError("answer-quality runs did not use the same dataset")

    rows: list[dict[str, Any]] = []
    for backend, result in zip(BACKENDS, results, strict=True):
        phases = {
            phase: latency_summary(tuple(getattr(case, field) for case in result.cases))
            for phase, field in (
                ("embedding", "embedding_ms"),
                ("retrieval", "retrieval_ms"),
                ("generation", "generation_ms"),
                ("end_to_end", "latency_ms"),
            )
        }
        rows.append(
            {
                "backend": backend,
                "case_count": result.case_count,
                "pass_rate": result.pass_rate,
                "acl_isolation_rate": result.acl_isolation_rate,
                "refusal_accuracy": result.refusal_accuracy,
                "citation_correctness": result.citation_correctness,
                "groundedness": result.groundedness,
                "answer_correctness": result.answer_correctness,
                "latency_ms": phases,
            }
        )

    limitations = [
        "Results use a synthetic policy corpus and a development-scale Azure deployment.",
        "Generation is non-deterministic; this run is evidence, not a universal quality claim.",
        "Backends ran sequentially to remain within the development model quota.",
        "Generation and end-to-end latency include quota retry/queue time in this development deployment.",
    ]
    comparison = {
        "dataset": results[0].dataset_name,
        "environment": "development",
        "results": rows,
        "limitations": limitations,
    }
    (args.input_dir / "comparison.json").write_text(
        json.dumps(comparison, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        f"# {args.title}",
        "",
        f"Dataset: `{results[0].dataset_name}` · Environment: development",
        "",
        "| Backend | Pass | ACL | Refusal | Citations | Grounded | Answer | E2E p50 | E2E p95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        *(
            f"| {row['backend']} | {row['pass_rate']:.4f} | "
            f"{row['acl_isolation_rate']:.4f} | {row['refusal_accuracy']:.4f} | "
            f"{row['citation_correctness']:.4f} | {row['groundedness']:.4f} | "
            f"{row['answer_correctness']:.4f} | "
            f"{row['latency_ms']['end_to_end']['p50']:.2f} ms | "
            f"{row['latency_ms']['end_to_end']['p95']:.2f} ms |"
            for row in rows
        ),
        "",
        "Latency phase distributions (mean, median, standard deviation, p50 and p95) are retained",
        "in `comparison.json`. Per-question outcomes and timings are in each backend artifact.",
        "",
        "## Interpretation guardrails",
        "",
        *[f"- {limitation}" for limitation in limitations],
        "",
    ]
    (args.input_dir / "comparison.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote answer-quality comparison to {args.input_dir}")


if __name__ == "__main__":
    main()
