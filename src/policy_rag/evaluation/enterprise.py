"""Deterministic enterprise-control and grounded-answer evaluation."""

from collections.abc import Callable, Sequence
from datetime import date
from statistics import mean
from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from policy_rag.answering import Answer, TimedAnswer


class EnterpriseEvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    control: Literal[
        "acl_isolation",
        "department_group_access",
        "effective_date",
        "policy_version",
        "unsupported_refusal",
        "citation_correctness",
        "grounded_answer",
    ]
    question: str = Field(min_length=3)
    user_groups: tuple[str, ...]
    as_of: date
    expected_refusal: bool
    expected_chunk_ids: tuple[str, ...] = ()
    forbidden_chunk_ids: tuple[str, ...] = ()
    required_answer_terms: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_expectation(self) -> "EnterpriseEvaluationCase":
        if self.expected_refusal and self.expected_chunk_ids:
            raise ValueError("refusal cases cannot require citations")
        return self


class EnterpriseEvaluationDataset(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    name: str
    mode: Literal["enterprise-controls"] = "enterprise-controls"
    cases: tuple[EnterpriseEvaluationCase, ...] = Field(min_length=1)


class EnterpriseCaseResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    control: str
    passed: bool
    refused: bool
    citation_correct: bool
    grounded: bool
    answer_correct: bool
    returned_chunk_ids: tuple[str, ...]
    forbidden_chunk_ids_returned: tuple[str, ...]
    latency_ms: float = Field(ge=0)
    embedding_ms: float = Field(default=0, ge=0)
    retrieval_ms: float = Field(default=0, ge=0)
    generation_ms: float = Field(default=0, ge=0)


class EnterpriseEvaluationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dataset_name: str
    case_count: int
    pass_rate: float = Field(ge=0, le=1)
    acl_isolation_rate: float = Field(ge=0, le=1)
    refusal_accuracy: float = Field(ge=0, le=1)
    citation_correctness: float = Field(ge=0, le=1)
    groundedness: float = Field(ge=0, le=1)
    answer_correctness: float = Field(ge=0, le=1)
    cases: tuple[EnterpriseCaseResult, ...]


def evaluate_enterprise_controls(
    dataset: EnterpriseEvaluationDataset,
    ask: Callable[[EnterpriseEvaluationCase], Answer | TimedAnswer],
) -> EnterpriseEvaluationResult:
    results: list[EnterpriseCaseResult] = []
    for case in dataset.cases:
        started = perf_counter()
        response = ask(case)
        measured_ms = (perf_counter() - started) * 1000
        if isinstance(response, TimedAnswer):
            answer = response.answer
            latency_ms = response.timings.end_to_end_ms
            embedding_ms = response.timings.embedding_ms
            retrieval_ms = response.timings.retrieval_ms
            generation_ms = response.timings.generation_ms
        else:
            answer = response
            latency_ms = measured_ms
            embedding_ms = retrieval_ms = generation_ms = 0.0
        returned = tuple(citation.chunk_id for citation in answer.citations)
        forbidden = tuple(item for item in returned if item in case.forbidden_chunk_ids)
        expected = set(case.expected_chunk_ids)
        citation_correct = not expected or expected.issubset(returned)
        grounded = answer.refused or (bool(answer.citations) and citation_correct and not forbidden)
        normalized = answer.answer.casefold()
        answer_correct = all(term.casefold() in normalized for term in case.required_answer_terms)
        refusal_correct = answer.refused == case.expected_refusal
        passed = (
            refusal_correct and citation_correct and grounded and answer_correct and not forbidden
        )
        results.append(
            EnterpriseCaseResult(
                case_id=case.case_id,
                control=case.control,
                passed=passed,
                refused=answer.refused,
                citation_correct=citation_correct,
                grounded=grounded,
                answer_correct=answer_correct,
                returned_chunk_ids=returned,
                forbidden_chunk_ids_returned=forbidden,
                latency_ms=latency_ms,
                embedding_ms=embedding_ms,
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
            )
        )

    def rate(selected: Sequence[EnterpriseCaseResult], attribute: str) -> float:
        return mean(bool(getattr(item, attribute)) for item in selected) if selected else 0.0

    acl_cases = [
        item for item in results if item.control in {"acl_isolation", "department_group_access"}
    ]
    refusal_cases = [item for item in results if item.control == "unsupported_refusal"]
    return EnterpriseEvaluationResult(
        dataset_name=dataset.name,
        case_count=len(results),
        pass_rate=rate(results, "passed"),
        acl_isolation_rate=rate(acl_cases, "passed"),
        refusal_accuracy=rate(refusal_cases, "passed"),
        citation_correctness=rate(results, "citation_correct"),
        groundedness=rate(results, "grounded"),
        answer_correctness=rate(results, "answer_correct"),
        cases=tuple(results),
    )
