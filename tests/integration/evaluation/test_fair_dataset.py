from pathlib import Path

from policy_rag.evaluation.models import EvaluationDataset
from policy_rag.ingestion.chunks import create_section_chunks
from policy_rag.ingestion.corpus import load_policy_corpus
from policy_rag.ingestion.sections import extract_policy_sections

CORPUS_ROOT = Path("data/synthetic/policies")
DATASET_PATH = Path("data/evaluation/fair-vector-v1.json")


def test_fair_vector_dataset_references_effective_authorised_canonical_chunks() -> None:
    corpus = load_policy_corpus(CORPUS_ROOT)
    chunks = {
        chunk.chunk_id: chunk
        for source in corpus
        for section in extract_policy_sections(source)
        for chunk in create_section_chunks(section)
    }
    dataset = EvaluationDataset.model_validate_json(DATASET_PATH.read_text(encoding="utf-8"))

    assert len(chunks) == 67
    assert len(dataset.cases) == 52
    assert len({case.case_id for case in dataset.cases}) == len(dataset.cases)
    assert len({case.question.casefold() for case in dataset.cases}) == len(dataset.cases)

    for case in dataset.cases:
        for chunk_id in case.relevant_chunk_ids:
            assert chunk_id in chunks, f"{case.case_id} references unknown chunk {chunk_id}"
            policy = chunks[chunk_id].section.policy
            assert policy.is_effective_on(case.as_of), (
                f"{case.case_id} references a policy version not effective on {case.as_of}"
            )
            assert policy.is_accessible_to(case.user_groups), (
                f"{case.case_id} cannot access its relevant chunk {chunk_id}"
            )
