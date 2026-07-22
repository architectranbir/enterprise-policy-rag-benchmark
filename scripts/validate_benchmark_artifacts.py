"""Validate committed benchmark JSON without executing a live benchmark."""

import json
from pathlib import Path

from policy_rag.evaluation.results import FairVectorRun

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    raw_paths = sorted((ROOT / "benchmark_results/raw").glob("*.json"))
    if not raw_paths:
        raise ValueError("no raw fair-vector artifacts found")
    runs = [
        FairVectorRun.model_validate_json(path.read_text(encoding="utf-8")) for path in raw_paths
    ]
    if any(run.mode != "fair-vector-only" for run in runs):
        raise ValueError("optimized run found in fair-vector artifact directory")
    comparison = json.loads(
        (ROOT / "benchmark_results/comparison/fair-vector-comparison.json").read_text(
            encoding="utf-8"
        )
    )
    if comparison.get("mode") != "fair-vector-only":
        raise ValueError("comparison mode is not fair-vector-only")
    print(f"Validated {len(runs)} fair-vector raw runs and one comparison artifact")


if __name__ == "__main__":
    main()
