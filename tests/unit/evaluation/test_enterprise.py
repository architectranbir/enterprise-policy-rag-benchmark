from pathlib import Path

from policy_rag.answering import Answer, Citation
from policy_rag.evaluation.enterprise import (
    EnterpriseEvaluationCase,
    EnterpriseEvaluationDataset,
    evaluate_enterprise_controls,
)


def test_enterprise_dataset_is_schema_valid_and_scores_controls() -> None:
    root = Path(__file__).resolve().parents[3]
    dataset = EnterpriseEvaluationDataset.model_validate_json(
        (root / "data/evaluation/enterprise-controls-v1.json").read_text(encoding="utf-8")
    )

    def ask(case: EnterpriseEvaluationCase) -> Answer:
        if case.expected_refusal:
            return Answer(answer="No evidence", refused=True, backend="test")
        chunk_id = case.expected_chunk_ids[0]
        return Answer(
            answer="The classification answer is GBP 250 once every three years. [1]",
            refused=False,
            backend="test",
            citations=(
                Citation(
                    number=1,
                    chunk_id=chunk_id,
                    document_id="POL",
                    document_title="Policy",
                    version="1.0",
                    section_id="SEC",
                    section_number="1",
                    section_title="Control",
                ),
            ),
        )

    result = evaluate_enterprise_controls(dataset, ask)
    assert result.case_count == 8
    assert result.acl_isolation_rate == 1.0
    assert result.refusal_accuracy == 1.0
    assert result.citation_correctness == 1.0
