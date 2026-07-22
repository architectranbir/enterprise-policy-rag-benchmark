"""Ingest the exact pre-embedded fair-vector artifact into one selected backend."""

import argparse
from pathlib import Path

from policy_rag.config import Settings
from policy_rag.evaluation.artifact import load_artifact
from policy_rag.runtime import build_runtime

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact",
        type=Path,
        default=ROOT / "data" / "generated" / "fair-vector-v1.json.gz",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact = load_artifact(args.artifact)
    settings = Settings()
    if settings.azure_openai_embedding_deployment != artifact.embedding_model:
        raise ValueError("configured embedding deployment does not match the artifact")
    runtime = build_runtime(settings)
    try:
        runtime.store.initialize()
        runtime.store.upsert(artifact.documents)
        backend = runtime.store.backend_name
    finally:
        runtime.close()
    print(f"Ingested {len(artifact.documents)} pre-embedded chunks into {backend}")


if __name__ == "__main__":
    main()
