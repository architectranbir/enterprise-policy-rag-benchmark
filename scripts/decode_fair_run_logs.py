"""Decode numbered fair-vector console-log records into a validated raw JSON artifact."""

import argparse
from pathlib import Path

from policy_rag.evaluation.results import decode_run_log_lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run = decode_run_log_lines(args.input.read_text(encoding="utf-8").splitlines())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(run.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Decoded {run.case_count} {run.backend} cases to {args.output}")


if __name__ == "__main__":
    main()
