"""Execute enterprise controls against one configured backend and persist raw evidence."""

import argparse
import csv
from pathlib import Path

from policy_rag.answering import TimedAnswer
from policy_rag.config import Settings
from policy_rag.domain.access import PolicyAccessContext
from policy_rag.evaluation.enterprise import (
    EnterpriseEvaluationCase,
    EnterpriseEvaluationDataset,
    evaluate_enterprise_controls,
)
from policy_rag.retrieval.models import PolicyRetrievalRequest
from policy_rag.runtime import build_runtime

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=ROOT / "data/evaluation/enterprise-controls-v1.json",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "benchmark_results/enterprise-controls"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = EnterpriseEvaluationDataset.model_validate_json(
        args.dataset.read_text(encoding="utf-8")
    )
    runtime = build_runtime(Settings())

    def ask(case: EnterpriseEvaluationCase) -> TimedAnswer:
        request = PolicyRetrievalRequest(
            access=PolicyAccessContext(
                user_id=f"benchmark:{case.case_id}",
                user_groups=case.user_groups,
                as_of=case.as_of,
            ),
            limit=5,
        )
        return runtime.service.ask_with_timings(case.question, request)

    try:
        result = evaluate_enterprise_controls(dataset, ask)
    finally:
        runtime.close()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    backend = runtime.store.backend_name
    (args.output_dir / f"{backend}.json").write_text(
        result.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    with (args.output_dir / f"{backend}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result.cases[0].model_fields))
        writer.writeheader()
        writer.writerows(item.model_dump(mode="json") for item in result.cases)
    (args.output_dir / f"{backend}.md").write_text(
        "\n".join(
            (
                f"# Enterprise controls: {backend}",
                "",
                f"- Cases: {result.case_count}",
                f"- Pass rate: {result.pass_rate:.4f}",
                f"- ACL isolation: {result.acl_isolation_rate:.4f}",
                f"- Refusal accuracy: {result.refusal_accuracy:.4f}",
                f"- Citation correctness: {result.citation_correctness:.4f}",
                f"- Groundedness: {result.groundedness:.4f}",
                f"- Answer correctness: {result.answer_correctness:.4f}",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(f"Wrote enterprise-control evidence for {backend} to {args.output_dir}")


if __name__ == "__main__":
    main()
