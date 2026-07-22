"""Verify keyless grounded answer generation against Microsoft Foundry."""

import json
import os
from datetime import date

from azure.identity import DefaultAzureCredential

from policy_rag.answering.foundry import FoundryAnswerProvider
from policy_rag.domain.policy import PolicyClassification
from policy_rag.retrieval.models import RetrievedPolicyChunk


def main() -> None:
    deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
    credential = DefaultAzureCredential()
    provider = FoundryAnswerProvider(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=deployment,
        credential=credential,
    )
    evidence = RetrievedPolicyChunk(
        chunk_id="SYN-SMOKE:1:SEC-001:CHK-001",
        text="Employees may claim up to GBP 250 for approved home-office equipment.",
        document_id="SYN-SMOKE",
        document_title="Synthetic Remote Working Policy",
        version="1",
        effective_from=date(2026, 1, 1),
        effective_to=None,
        department="Human Resources",
        classification=PolicyClassification.INTERNAL,
        section_id="SYN-SMOKE:1:SEC-001",
        section_number="1",
        section_title="Equipment",
        section_ordinal=1,
        chunk_ordinal=1,
        score=1.0,
    )
    try:
        answer = provider.generate("How much can employees claim for equipment?", (evidence,))
    finally:
        credential.close()
    if "[1]" not in answer:
        raise RuntimeError("Foundry answer did not cite the supplied evidence marker")
    print(json.dumps({"deployment": deployment, "answer": answer}, indent=2))


if __name__ == "__main__":
    main()
