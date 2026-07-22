from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    number: int = Field(ge=1)
    chunk_id: str
    document_id: str
    document_title: str
    version: str
    section_id: str
    section_number: str
    section_title: str


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    answer: str = Field(min_length=1)
    citations: tuple[Citation, ...] = ()
    refused: bool
    backend: str


class AnswerTimings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    embedding_ms: float = Field(ge=0)
    retrieval_ms: float = Field(ge=0)
    generation_ms: float = Field(ge=0)
    end_to_end_ms: float = Field(ge=0)


class TimedAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    answer: Answer
    timings: AnswerTimings
