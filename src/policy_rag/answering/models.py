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
