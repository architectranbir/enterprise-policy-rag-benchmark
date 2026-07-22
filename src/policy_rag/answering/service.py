import re

from policy_rag.answering.models import Answer, Citation
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
        vector = self._embeddings.embed((question,))[0]
        evidence = self._store.retrieve(request.model_copy(update={"query_embedding": vector}))
        if not evidence:
            return Answer(answer=REFUSAL, refused=True, backend=self._store.backend_name)
        text = self._answers.generate(question, evidence)
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
            return Answer(
                answer=REFUSAL,
                citations=(),
                refused=True,
                backend=self._store.backend_name,
            )
        return Answer(
            answer=text,
            citations=() if refused else citations,
            refused=refused,
            backend=self._store.backend_name,
        )
