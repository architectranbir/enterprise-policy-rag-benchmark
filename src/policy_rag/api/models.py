from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from policy_rag.answering import Answer
from policy_rag.domain.policy import PolicyClassification


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    question: str = Field(min_length=3, max_length=2000)
    as_of: date
    document_id: str | None = None
    department: str | None = None
    classification: PolicyClassification | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class AskResponse(Answer):
    correlation_id: str


class HealthResponse(BaseModel):
    status: str
    backend: str
