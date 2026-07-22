from collections.abc import Callable, Sequence
from dataclasses import dataclass
from math import log2
from statistics import mean, median, pstdev
from time import perf_counter

from policy_rag.evaluation.models import EvaluationCase


@dataclass(frozen=True)
class EvaluationResult:
    cases: int
    recall_at_k: float
    mean_reciprocal_rank: float
    mean_latency_ms: float
    precision_at_k: float = 0.0
    ndcg_at_k: float = 0.0
    median_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    latency_stddev_ms: float = 0.0


def retrieval_metrics(
    relevant_chunk_ids: Sequence[str], retrieved_chunk_ids: Sequence[str]
) -> tuple[float, float, float, float]:
    relevant = set(relevant_chunk_ids)
    retrieved = tuple(retrieved_chunk_ids)
    if not relevant:
        return 0.0, 0.0, 0.0, 0.0
    hits = [1 if item in relevant else 0 for item in retrieved]
    recall = sum(hits) / len(relevant)
    precision = sum(hits) / len(retrieved) if retrieved else 0.0
    reciprocal_rank = next((1 / rank for rank, hit in enumerate(hits, 1) if hit), 0.0)
    dcg = sum(hit / log2(rank + 1) for rank, hit in enumerate(hits, 1))
    ideal_hits = min(len(relevant), len(retrieved))
    ideal_dcg = sum(1 / log2(rank + 1) for rank in range(1, ideal_hits + 1))
    ndcg = dcg / ideal_dcg if ideal_dcg else 0.0
    return recall, precision, reciprocal_rank, ndcg


def _percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def evaluate_retrieval(
    cases: Sequence[EvaluationCase],
    retrieve: Callable[[EvaluationCase], Sequence[str]],
    *,
    warmup_requests: int = 0,
    repetitions: int = 1,
) -> EvaluationResult:
    if warmup_requests < 0 or repetitions < 1:
        raise ValueError("warmup_requests must be non-negative and repetitions must be positive")
    if cases:
        for index in range(warmup_requests):
            retrieve(cases[index % len(cases)])
    recalls: list[float] = []
    precisions: list[float] = []
    reciprocal_ranks: list[float] = []
    ndcgs: list[float] = []
    latencies: list[float] = []
    for _ in range(repetitions):
        for case in cases:
            started = perf_counter()
            retrieved = tuple(retrieve(case))
            latencies.append((perf_counter() - started) * 1000)
            recall, precision, reciprocal_rank, ndcg = retrieval_metrics(
                case.relevant_chunk_ids, retrieved
            )
            recalls.append(recall)
            precisions.append(precision)
            reciprocal_ranks.append(reciprocal_rank)
            ndcgs.append(ndcg)
    count = len(cases) * repetitions
    if count == 0:
        return EvaluationResult(0, 0.0, 0.0, 0.0)
    return EvaluationResult(
        cases=count,
        recall_at_k=mean(recalls),
        mean_reciprocal_rank=mean(reciprocal_ranks),
        mean_latency_ms=mean(latencies),
        precision_at_k=mean(precisions),
        ndcg_at_k=mean(ndcgs),
        median_latency_ms=median(latencies),
        p50_latency_ms=_percentile(latencies, 0.5),
        p95_latency_ms=_percentile(latencies, 0.95),
        latency_stddev_ms=pstdev(latencies),
    )
