"""Run one grounded answer smoke test against the selected VECTOR_BACKEND."""

import json
from datetime import date

from policy_rag.config import Settings
from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyClassification
from policy_rag.retrieval import PolicyRetrievalRequest
from policy_rag.runtime import build_runtime

QUESTION = "How much may an employee claim for home-office equipment?"


def main() -> None:
    settings = Settings()
    runtime = build_runtime(settings)
    request = PolicyRetrievalRequest(
        access=PolicyAccessContext(
            user_id="backend-smoke-test",
            user_groups=("employees",),
            as_of=date(2026, 7, 20),
        ),
        document_id="POL-HR-001",
        classification=PolicyClassification.INTERNAL,
        limit=5,
    )
    try:
        result = runtime.service.ask(QUESTION, request)
    finally:
        runtime.close()

    if result.refused:
        raise RuntimeError(f"{result.backend} refused a supported synthetic-policy question")
    if not result.citations:
        raise RuntimeError(f"{result.backend} returned an answer without citations")
    if any(citation.document_id != "POL-HR-001" for citation in result.citations):
        raise RuntimeError(f"{result.backend} cited an unexpected policy document")

    print(
        json.dumps(
            {
                "backend": result.backend,
                "question": QUESTION,
                "answer": result.answer,
                "refused": result.refused,
                "citation_count": len(result.citations),
                "citation_chunk_ids": [citation.chunk_id for citation in result.citations],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
