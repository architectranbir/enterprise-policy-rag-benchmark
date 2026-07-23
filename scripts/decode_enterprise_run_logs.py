"""Decode numbered enterprise-evaluation console records into validated artifacts."""

import argparse
import base64
import csv
import gzip
import re
import sys
from pathlib import Path

from policy_rag.evaluation.enterprise import EnterpriseEvaluationResult

PART_PATTERN = re.compile(r"ENTERPRISE_RUN_PART=(\d+)/(\d+):([A-Za-z0-9+/=]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parts: dict[int, str] = {}
    total: int | None = None
    for line in sys.stdin.read().splitlines():
        match = PART_PATTERN.fullmatch(line.strip())
        if match is None:
            continue
        index, line_total, payload = int(match.group(1)), int(match.group(2)), match.group(3)
        if total is not None and line_total != total:
            raise ValueError("enterprise log parts disagree on total part count")
        total = line_total
        if index in parts:
            raise ValueError(f"duplicate enterprise log part {index}")
        parts[index] = payload
    if total is None or set(parts) != set(range(1, total + 1)):
        raise ValueError("enterprise run log parts are missing or incomplete")
    payload = gzip.decompress(
        base64.b64decode("".join(parts[index] for index in range(1, total + 1)))
    )
    result = EnterpriseEvaluationResult.model_validate_json(payload)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    with args.output.with_suffix(".csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(type(result.cases[0]).model_fields))
        writer.writeheader()
        writer.writerows(item.model_dump(mode="json") for item in result.cases)
    args.output.with_suffix(".md").write_text(
        "\n".join(
            (
                f"# {result.dataset_name}",
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
    print(f"Decoded {result.case_count} cases to {args.output}")


if __name__ == "__main__":
    main()
