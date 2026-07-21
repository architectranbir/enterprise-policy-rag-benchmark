from collections.abc import Callable, Sequence
from dataclasses import dataclass
from time import perf_counter

from policy_rag.evaluation.models import EvaluationCase


@dataclass(frozen=True)
class EvaluationResult:
    cases: int
    recall_at_k: float
    mean_reciprocal_rank: float
    mean_latency_ms: float


def evaluate_retrieval(
    cases: Sequence[EvaluationCase], retrieve: Callable[[EvaluationCase], Sequence[str]]
) -> EvaluationResult:
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    latencies: list[float] = []
    for case in cases:
        started = perf_counter()
        retrieved = tuple(retrieve(case))
        latencies.append((perf_counter() - started) * 1000)
        relevant = set(case.relevant_chunk_ids)
        recalls.append(len(relevant.intersection(retrieved)) / len(relevant))
        reciprocal_ranks.append(
            next((1 / rank for rank, item in enumerate(retrieved, 1) if item in relevant), 0.0)
        )
    count = len(cases)
    if count == 0:
        return EvaluationResult(0, 0.0, 0.0, 0.0)
    return EvaluationResult(
        count, sum(recalls) / count, sum(reciprocal_ranks) / count, sum(latencies) / count
    )
