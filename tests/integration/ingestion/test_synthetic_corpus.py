from pathlib import Path

from policy_rag.ingestion.corpus import load_policy_corpus

CORPUS_ROOT = Path("data/synthetic/policies")


def test_committed_synthetic_policy_corpus_is_valid() -> None:
    """Verify that the policy corpus committed to the repository is valid."""

    corpus = load_policy_corpus(CORPUS_ROOT)

    assert len(corpus) == 9
    assert len({source.metadata.document_id for source in corpus}) == 8

    source = next(
        source
        for source in corpus
        if source.metadata.document_id == "POL-HR-001" and source.metadata.version == "1.0"
    )

    assert source.metadata.document_id == "POL-HR-001"
    assert source.metadata.version == "1.0"
    assert source.metadata.title == "Remote Working Policy"
    assert source.content.startswith("# Remote Working Policy")

    travel_versions = {
        source.metadata.version for source in corpus if source.metadata.document_id == "POL-FIN-001"
    }
    assert travel_versions == {"1.0", "2.0"}
