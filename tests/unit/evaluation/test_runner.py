from datetime import date

from policy_rag.evaluation.models import EvaluationCase
from policy_rag.evaluation.runner import evaluate_retrieval, retrieval_metrics


def test_calculates_recall_and_mrr_without_inventing_results() -> None:
    cases = (
        EvaluationCase(
            case_id="one",
            question="Where is it?",
            user_groups=("employees",),
            as_of=date(2026, 7, 22),
            relevant_chunk_ids=("a", "b"),
        ),
    )
    result = evaluate_retrieval(cases, lambda _: ("x", "a"))
    assert result.cases == 1
    assert result.recall_at_k == 0.5
    assert result.mean_reciprocal_rank == 0.5
    assert result.mean_latency_ms >= 0


def test_calculates_precision_ndcg_and_repeated_latency() -> None:
    assert retrieval_metrics(("a", "b"), ("x", "a")) == (0.5, 0.5, 0.5, 0.38685280723454163)
    case = EvaluationCase(
        case_id="one",
        question="Where is it?",
        user_groups=("employees",),
        as_of=date(2026, 7, 22),
        relevant_chunk_ids=("a",),
    )
    calls = 0

    def retrieve(_: EvaluationCase) -> tuple[str, ...]:
        nonlocal calls
        calls += 1
        return ("a",)

    result = evaluate_retrieval((case,), retrieve, warmup_requests=2, repetitions=3)
    assert calls == 5
    assert result.cases == 3
    assert result.precision_at_k == result.ndcg_at_k == 1.0
    assert result.p95_latency_ms >= 0
