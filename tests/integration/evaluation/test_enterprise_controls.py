from pathlib import Path

from policy_rag.domain.chunk import PolicyChunk
from policy_rag.evaluation.enterprise import EnterpriseEvaluationDataset
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.corpus import load_policy_corpus
from policy_rag.ingestion.sections import extract_policy_sections


def test_enterprise_controls_reference_real_access_and_version_boundaries() -> None:
    chunks = {
        chunk.chunk_id: chunk
        for source in load_policy_corpus(Path("data/synthetic/policies"))
        for section in extract_policy_sections(source)
        for chunk in create_section_chunks(section)
    }
    for dataset_path in (
        Path("data/evaluation/enterprise-controls-v1.json"),
        Path("data/evaluation/end-to-end-v1.json"),
    ):
        _assert_dataset(dataset_path, chunks)


def _assert_dataset(dataset_path: Path, chunks: dict[str, PolicyChunk]) -> None:
    dataset = EnterpriseEvaluationDataset.model_validate_json(
        dataset_path.read_text(encoding="utf-8")
    )
    assert len({case.case_id for case in dataset.cases}) == len(dataset.cases)
    for case in dataset.cases:
        for chunk_id in case.expected_chunk_ids:
            assert chunk_id in chunks
            policy = chunks[chunk_id].section.policy
            assert policy.is_effective_on(case.as_of)
            assert policy.is_accessible_to(case.user_groups)
        for chunk_id in case.forbidden_chunk_ids:
            assert chunk_id in chunks
            policy = chunks[chunk_id].section.policy
            assert not (
                policy.is_effective_on(case.as_of) and policy.is_accessible_to(case.user_groups)
            )
