"""Read durable, schema-validated benchmark artifacts for the Web Benchmark Lab."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from policy_rag.evaluation.enterprise import EnterpriseEvaluationResult
from policy_rag.evaluation.results import FairVectorRun


class BenchmarkRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str
    mode: str
    backend: str
    dataset: str
    top_k: int | None
    repetitions: int
    recall_at_k: float | None
    precision_at_k: float | None
    mrr: float | None
    ndcg_at_k: float | None
    mean_latency_ms: float | None
    p50_latency_ms: float | None
    p95_latency_ms: float | None
    created_at: str
    pass_rate: float | None = None
    acl_isolation_rate: float | None = None
    refusal_accuracy: float | None = None
    citation_correctness: float | None = None
    groundedness: float | None = None
    answer_correctness: float | None = None


class BenchmarkLabRepository:
    """Filesystem artifact repository; no synthetic fallback values are produced."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def list_runs(self) -> tuple[BenchmarkRunSummary, ...]:
        runs: list[BenchmarkRunSummary] = []
        retrieval_tracks = (
            ("fair-vector-only", self._root / "raw"),
            ("platform-optimized", self._root / "platform-optimized" / "raw"),
        )
        for track, directory in retrieval_tracks:
            for path in sorted(directory.glob("*.json")):
                payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
                run = FairVectorRun.model_validate(payload)
                if run.mode != track:
                    raise ValueError(f"{path} is stored under the wrong benchmark track")
                runs.append(self._summary(f"{track}--{path.stem}", run, payload))
        for track in ("enterprise-controls", "end-to-end"):
            paths = (
                self._root / track / f"{backend}.json"
                for backend in ("azure_ai_search", "pgvector", "qdrant")
            )
            for path in paths:
                if not path.is_file():
                    continue
                result = EnterpriseEvaluationResult.model_validate_json(
                    path.read_text(encoding="utf-8")
                )
                runs.append(
                    self._enterprise_summary(f"{track}--{path.stem}", track, path.stem, result)
                )
        return tuple(sorted(runs, key=lambda item: item.created_at, reverse=True))

    def raw_run(self, run_id: str) -> dict[str, Any]:
        if not run_id.replace("_", "").replace("-", "").isalnum():
            raise ValueError("invalid benchmark run ID")
        try:
            track, backend = run_id.split("--", 1)
        except ValueError as error:
            raise FileNotFoundError(run_id) from error
        directories = {
            "fair-vector-only": self._root / "raw",
            "platform-optimized": self._root / "platform-optimized" / "raw",
            "enterprise-controls": self._root / "enterprise-controls",
            "end-to-end": self._root / "end-to-end",
        }
        if track not in directories:
            raise FileNotFoundError(run_id)
        path = directories[track] / f"{backend}.json"
        if not path.is_file():
            raise FileNotFoundError(run_id)
        model = (
            EnterpriseEvaluationResult
            if track in {"enterprise-controls", "end-to-end"}
            else FairVectorRun
        )
        run = model.model_validate_json(path.read_text(encoding="utf-8"))
        payload: dict[str, Any] = json.loads(run.model_dump_json())
        payload["backend"] = backend
        payload["mode"] = track
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

    @staticmethod
    def _enterprise_summary(
        run_id: str,
        mode: str,
        backend: str,
        result: EnterpriseEvaluationResult,
    ) -> BenchmarkRunSummary:
        latencies = [item.latency_ms for item in result.cases]
        return BenchmarkRunSummary(
            run_id=run_id,
            mode=mode,
            backend=backend,
            dataset=result.dataset_name,
            top_k=None,
            repetitions=1,
            recall_at_k=None,
            precision_at_k=None,
            mrr=None,
            ndcg_at_k=None,
            mean_latency_ms=sum(latencies) / len(latencies),
            p50_latency_ms=None,
            p95_latency_ms=None,
            created_at="",
            pass_rate=result.pass_rate,
            acl_isolation_rate=result.acl_isolation_rate,
            refusal_accuracy=result.refusal_accuracy,
            citation_correctness=result.citation_correctness,
            groundedness=result.groundedness,
            answer_correctness=result.answer_correctness,
        )
