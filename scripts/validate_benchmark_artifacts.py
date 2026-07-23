"""Validate committed benchmark evidence without executing live services."""

import json
from pathlib import Path

from policy_rag.evaluation.enterprise import EnterpriseEvaluationResult
from policy_rag.evaluation.results import FairVectorRun

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmark_results"
BACKENDS = {"azure_ai_search", "pgvector", "qdrant"}


def validate_retrieval_track(
    *, mode: str, raw_dir: Path, comparison: Path
) -> tuple[FairVectorRun, ...]:
    paths = sorted(raw_dir.glob("*.json"))
    if {path.stem for path in paths} != BACKENDS:
        raise ValueError(f"{mode} must contain exactly one raw run for each backend")
    runs = tuple(
        FairVectorRun.model_validate_json(path.read_text(encoding="utf-8")) for path in paths
    )
    if any(run.mode != mode for run in runs):
        raise ValueError(f"run stored under the wrong {mode} directory")
    signatures = {
        (run.artifact_sha256, run.source_sha256, run.dataset_name, run.top_k, run.case_count)
        for run in runs
    }
    if len(signatures) != 1:
        raise ValueError(f"{mode} backend inputs are not comparable")
    if any(run.measured_repetitions != 3 or run.measurement_count != 156 for run in runs):
        raise ValueError(f"{mode} must contain 52 questions and three measured repetitions")
    for path in paths:
        if not path.with_suffix(".csv").is_file() or not path.with_suffix(".md").is_file():
            raise ValueError(f"{path} is missing its CSV or Markdown companion")
    payload = json.loads(comparison.read_text(encoding="utf-8"))
    if payload.get("mode") != mode or payload.get("runs_per_backend") != 3:
        raise ValueError(f"{mode} comparison metadata does not match raw evidence")
    return runs


def validate_answer_track(
    directory: Path, expected_cases: int
) -> tuple[EnterpriseEvaluationResult, ...]:
    paths = [directory / f"{backend}.json" for backend in sorted(BACKENDS)]
    if not all(path.is_file() for path in paths):
        raise ValueError(f"{directory.name} must contain one result for each backend")
    results = tuple(
        EnterpriseEvaluationResult.model_validate_json(path.read_text(encoding="utf-8"))
        for path in paths
    )
    if any(result.case_count != expected_cases for result in results):
        raise ValueError(f"{directory.name} case count does not match the published methodology")
    if len({result.dataset_name for result in results}) != 1:
        raise ValueError(f"{directory.name} backends did not use the same dataset")
    for path in paths:
        if not path.with_suffix(".csv").is_file() or not path.with_suffix(".md").is_file():
            raise ValueError(f"{path} is missing its CSV or Markdown companion")
    comparison = json.loads((directory / "comparison.json").read_text(encoding="utf-8"))
    if (
        comparison.get("dataset") != results[0].dataset_name
        or len(comparison.get("results", [])) != 3
    ):
        raise ValueError(f"{directory.name} comparison does not match backend evidence")
    return results


def main() -> None:
    fair = validate_retrieval_track(
        mode="fair-vector-only",
        raw_dir=RESULTS / "raw",
        comparison=RESULTS / "comparison/fair-vector-comparison.json",
    )
    optimized = validate_retrieval_track(
        mode="platform-optimized",
        raw_dir=RESULTS / "platform-optimized/raw",
        comparison=RESULTS / "platform-optimized/comparison/platform-comparison.json",
    )
    controls = validate_answer_track(RESULTS / "enterprise-controls", 8)
    end_to_end = validate_answer_track(RESULTS / "end-to-end", 12)
    total = sum(run.measurement_count for run in (*fair, *optimized))
    total += sum(result.case_count for result in (*controls, *end_to_end))
    if total != 996:
        raise ValueError(f"expected 996 measured executions, found {total}")
    print("Validated 996 measured executions across four isolated benchmark tracks")


if __name__ == "__main__":
    main()
