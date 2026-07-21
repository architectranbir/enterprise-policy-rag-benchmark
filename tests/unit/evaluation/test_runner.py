from policy_rag.evaluation.models import EvaluationCase
from policy_rag.evaluation.runner import evaluate_retrieval


def test_calculates_recall_and_mrr_without_inventing_results() -> None:
    cases = (
        EvaluationCase(
            case_id="one",
            question="Where is it?",
            user_groups=("employees",),
            relevant_chunk_ids=("a", "b"),
        ),
    )
    result = evaluate_retrieval(cases, lambda _: ("x", "a"))
    assert result.cases == 1
    assert result.recall_at_k == 0.5
    assert result.mean_reciprocal_rank == 0.5
    assert result.mean_latency_ms >= 0
