from pydantic import BaseModel, ConfigDict, Field


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    case_id: str
    question: str = Field(min_length=3)
    user_groups: tuple[str, ...]
    relevant_chunk_ids: tuple[str, ...] = Field(min_length=1)


class EvaluationDataset(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    mode: str = Field(pattern="^fair-vector-only$")
    embedding_model: str
    embedding_dimensions: int
    similarity_metric: str = Field(pattern="^cosine$")
    top_k: int
    cases: tuple[EvaluationCase, ...]
