import json
from pathlib import Path

from fastapi.testclient import TestClient

from policy_rag.api.app import create_app
from policy_rag.api.benchmark_lab import BenchmarkLabRepository


def test_benchmark_lab_has_honest_empty_state(tmp_path: Path) -> None:
    client = TestClient(create_app(benchmark_repository=BenchmarkLabRepository(tmp_path)))
    assert client.get("/benchmarks/runs").json() == []
    assert client.post("/benchmarks/runs").status_code == 503


def test_benchmark_lab_lists_and_exports_schema_valid_run(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[3] / "benchmark_results/raw/qdrant.json"
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "qdrant.json").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    client = TestClient(create_app(benchmark_repository=BenchmarkLabRepository(tmp_path)))
    runs = client.get("/benchmarks/runs").json()
    assert runs[0]["backend"] == "qdrant"
    assert runs[0]["p50_latency_ms"] is not None
    assert runs[0]["ndcg_at_k"] is not None
    exported = client.get("/benchmarks/runs/fair-vector-only--qdrant")
    assert exported.status_code == 200
    assert json.loads(exported.text)["backend"] == "qdrant"
    assert client.get("/benchmarks/runs/../secret").status_code == 404


def test_benchmark_lab_keeps_tracks_separate(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3] / "benchmark_results"
    sources = {
        tmp_path / "raw" / "qdrant.json": root / "raw" / "qdrant.json",
        tmp_path / "platform-optimized" / "raw" / "qdrant.json": (
            root / "platform-optimized" / "raw" / "qdrant.json"
        ),
        tmp_path / "enterprise-controls" / "qdrant.json": (
            root / "enterprise-controls" / "qdrant.json"
        ),
    }
    for target, source in sources.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    repository = BenchmarkLabRepository(tmp_path)
    runs = repository.list_runs()
    assert {run.mode for run in runs} == {
        "fair-vector-only",
        "platform-optimized",
        "enterprise-controls",
    }
    controls = next(run for run in runs if run.mode == "enterprise-controls")
    assert controls.recall_at_k is None
    assert controls.pass_rate is not None
