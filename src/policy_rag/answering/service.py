import re
from time import perf_counter

from policy_rag.answering.models import Answer, AnswerTimings, Citation, TimedAnswer
from policy_rag.answering.provider import AnswerProvider
from policy_rag.embeddings import EmbeddingProvider
from policy_rag.retrieval.base import PolicyVectorStore
from policy_rag.retrieval.models import PolicyRetrievalRequest

REFUSAL = "I cannot answer this question from the available policy evidence."


class PolicyAnswerService:
    def __init__(
        self, store: PolicyVectorStore, embeddings: EmbeddingProvider, answers: AnswerProvider
    ) -> None:
        self._store = store
        self._embeddings = embeddings
        self._answers = answers

    def ask(self, question: str, request: PolicyRetrievalRequest) -> Answer:
        return self.ask_with_timings(question, request).answer

    def ask_with_timings(self, question: str, request: PolicyRetrievalRequest) -> TimedAnswer:
        end_to_end_started = perf_counter()
        embedding_started = perf_counter()
        vector = self._embeddings.embed((question,))[0]
        embedding_ms = (perf_counter() - embedding_started) * 1000
        retrieval_started = perf_counter()
        evidence = self._store.retrieve(request.model_copy(update={"query_embedding": vector}))
        retrieval_ms = (perf_counter() - retrieval_started) * 1000
        generation_ms = 0.0
        if not evidence:
            answer = Answer(answer=REFUSAL, refused=True, backend=self._store.backend_name)
            return self._timed(
                answer, embedding_ms, retrieval_ms, generation_ms, end_to_end_started
            )
        generation_started = perf_counter()
        text = self._answers.generate(question, evidence)
        generation_ms = (perf_counter() - generation_started) * 1000
        all_citations = tuple(
            Citation(
                number=index,
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                document_title=item.document_title,
                version=item.version,
                section_id=item.section_id,
                section_number=item.section_number,
                section_title=item.section_title,
            )
            for index, item in enumerate(evidence, 1)
        )
        refused = text == REFUSAL
        cited_numbers = {int(value) for value in re.findall(r"\[(\d+)]", text)}
        citations = tuple(item for item in all_citations if item.number in cited_numbers)
        if not refused and not citations:
            answer = Answer(
                answer=REFUSAL,
                citations=(),
                refused=True,
                backend=self._store.backend_name,
            )
            return self._timed(
                answer, embedding_ms, retrieval_ms, generation_ms, end_to_end_started
            )
        answer = Answer(
            answer=text,
            citations=() if refused else citations,
            refused=refused,
            backend=self._store.backend_name,
        )
        return self._timed(answer, embedding_ms, retrieval_ms, generation_ms, end_to_end_started)

    @staticmethod
    def _timed(
        answer: Answer,
        embedding_ms: float,
        retrieval_ms: float,
        generation_ms: float,
        end_to_end_started: float,
    ) -> TimedAnswer:
        return TimedAnswer(
            answer=answer,
            timings=AnswerTimings(
                embedding_ms=embedding_ms,
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
                end_to_end_ms=(perf_counter() - end_to_end_started) * 1000,
            ),
        )
