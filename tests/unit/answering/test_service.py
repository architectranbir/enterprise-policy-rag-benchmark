from collections.abc import Sequence
from datetime import date

from policy_rag.answering.service import REFUSAL, PolicyAnswerService
from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification
from policy_rag.embeddings import EmbeddingVector
from policy_rag.indexing import IndexedPolicyChunk
from policy_rag.retrieval.models import PolicyRetrievalRequest, RetrievedPolicyChunk


class Embeddings:
    dimensions = 2

    def embed(self, texts: Sequence[str], /) -> tuple[EmbeddingVector, ...]:
        return ((0.1, 0.2),)


class Answers:
    def generate(self, question: str, evidence: Sequence[RetrievedPolicyChunk]) -> str:
        return "Employees may claim GBP 250. [1]"


class UncitedAnswers:
    def generate(self, question: str, evidence: Sequence[RetrievedPolicyChunk]) -> str:
        return "Employees may claim GBP 250."


class Store:
    backend_name = "test"

    def __init__(self, results: tuple[RetrievedPolicyChunk, ...]) -> None:
        self.results = results
        self.request: PolicyRetrievalRequest | None = None

    def upsert(self, documents: tuple[IndexedPolicyChunk, ...]) -> None:
        pass

    def initialize(self) -> None:
        pass

    def retrieve(self, request: PolicyRetrievalRequest) -> tuple[RetrievedPolicyChunk, ...]:
        self.request = request
        return self.results

    def ready(self) -> bool:
        return True

    def close(self) -> None:
        pass


def request() -> PolicyRetrievalRequest:
    return PolicyRetrievalRequest(
        access=PolicyAccessContext(
            user_id="user", user_groups=("employees",), as_of=date(2026, 1, 1)
        )
    )


def result() -> RetrievedPolicyChunk:
    return RetrievedPolicyChunk(
        chunk_id="POL:1:SEC:CHK",
        text="Evidence",
        document_id="POL",
        document_title="Policy",
        version="1",
        effective_from=date(2026, 1, 1),
        effective_to=None,
        department="HR",
        classification=PolicyClassification.INTERNAL,
        section_id="POL:1:SEC",
        section_number="1",
        section_title="Expenses",
        section_ordinal=1,
        chunk_ordinal=1,
        score=0.9,
    )


def test_generates_grounded_answer_and_structured_citation() -> None:
    store = Store((result(),))
    answer = PolicyAnswerService(store, Embeddings(), Answers()).ask("What can I claim?", request())
    assert answer.answer.endswith("[1]")
    assert answer.citations[0].chunk_id == result().chunk_id
    assert store.request is not None and store.request.query_embedding == (0.1, 0.2)


def test_reports_embedding_retrieval_generation_and_end_to_end_timings() -> None:
    timed = PolicyAnswerService(Store((result(),)), Embeddings(), Answers()).ask_with_timings(
        "What can I claim?", request()
    )
    assert timed.answer.refused is False
    assert timed.timings.end_to_end_ms >= (
        timed.timings.embedding_ms + timed.timings.retrieval_ms + timed.timings.generation_ms
    )


def test_refuses_without_evidence_and_does_not_generate() -> None:
    answer = PolicyAnswerService(Store(()), Embeddings(), Answers()).ask("Unknown?", request())
    assert answer.refused is True
    assert answer.answer == REFUSAL
    assert answer.citations == ()


def test_refuses_generated_answer_without_a_valid_evidence_citation() -> None:
    answer = PolicyAnswerService(Store((result(),)), Embeddings(), UncitedAnswers()).ask(
        "What can I claim?", request()
    )
    assert answer.refused is True
    assert answer.answer == REFUSAL
    assert answer.citations == ()
