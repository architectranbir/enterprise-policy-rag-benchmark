from collections.abc import Sequence
from typing import Protocol

from policy_rag.retrieval.models import RetrievedPolicyChunk


class AnswerProvider(Protocol):
    def generate(self, question: str, evidence: Sequence[RetrievedPolicyChunk]) -> str: ...
