"""Read durable, schema-validated benchmark artifacts for the Web Benchmark Lab."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from policy_rag.evaluation.results import FairVectorRun


class BenchmarkRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str
    mode: str
    backend: str
    dataset: str
    top_k: int
    repetitions: int
    recall_at_k: float
    precision_at_k: float | None
    mrr: float
    ndcg_at_k: float | None
    mean_latency_ms: float
    p50_latency_ms: float | None
    p95_latency_ms: float | None
    created_at: str


class BenchmarkLabRepository:
    """Filesystem artifact repository; no synthetic fallback values are produced."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def list_runs(self) -> tuple[BenchmarkRunSummary, ...]:
        runs: list[BenchmarkRunSummary] = []
        for path in sorted((self._root / "raw").glob("*.json")):
            payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
            run = FairVectorRun.model_validate(payload)
            runs.append(self._summary(path.stem, run, payload))
        return tuple(sorted(runs, key=lambda item: item.created_at, reverse=True))

    def raw_run(self, run_id: str) -> dict[str, Any]:
        if not run_id.replace("_", "").replace("-", "").isalnum():
            raise ValueError("invalid benchmark run ID")
        path = self._root / "raw" / f"{run_id}.json"
        if not path.is_file():
            raise FileNotFoundError(run_id)
        run = FairVectorRun.model_validate_json(path.read_text(encoding="utf-8"))
        payload: dict[str, Any] = json.loads(run.model_dump_json())
        return payload

    @staticmethod
    def _summary(
        run_id: str, run: FairVectorRun, source_payload: dict[str, Any]
    ) -> BenchmarkRunSummary:
        return BenchmarkRunSummary(
            run_id=run_id,
            mode=run.mode,
            backend=run.backend,
            dataset=run.dataset_name,
            top_k=run.top_k,
            repetitions=run.measured_repetitions,
            recall_at_k=run.recall_at_k,
            precision_at_k=(run.precision_at_k if "precision_at_k" in source_payload else None),
            mrr=run.mean_reciprocal_rank,
            ndcg_at_k=run.ndcg_at_k if "ndcg_at_k" in source_payload else None,
            mean_latency_ms=run.mean_latency_ms,
            p50_latency_ms=run.p50_latency_ms if "p50_latency_ms" in source_payload else None,
            p95_latency_ms=run.p95_latency_ms if "p95_latency_ms" in source_payload else None,
            created_at=run.created_at.isoformat(),
        )
