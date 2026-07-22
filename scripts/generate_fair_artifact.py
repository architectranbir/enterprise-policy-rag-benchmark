"""Generate canonical document and query embeddings exactly once for all backends."""

import argparse
from pathlib import Path

from azure.identity import DefaultAzureCredential

from policy_rag.config import Settings
from policy_rag.embeddings import FoundryEmbeddingProvider
from policy_rag.evaluation.artifact import create_fair_vector_artifact, write_artifact
from policy_rag.evaluation.models import EvaluationDataset

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "generated" / "fair-vector-v1.json.gz",
    )
    parser.add_argument("--batch-size", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings()
    dataset_path = ROOT / "data" / "evaluation" / "fair-vector-v1.json"
    dataset = EvaluationDataset.model_validate_json(dataset_path.read_text(encoding="utf-8"))
    if settings.azure_openai_embedding_deployment != dataset.embedding_model:
        raise ValueError("configured embedding deployment does not match the evaluation dataset")
    credential = DefaultAzureCredential()
    provider = FoundryEmbeddingProvider(
        endpoint=settings.azure_openai_endpoint,
        deployment=settings.azure_openai_embedding_deployment,
        credential=credential,
    )
    try:
        artifact = create_fair_vector_artifact(
            corpus_root=ROOT / "data" / "synthetic" / "policies",
            dataset_path=dataset_path,
            provider=provider,
            batch_size=args.batch_size,
        )
        write_artifact(args.output, artifact)
    finally:
        credential.close()
    print(
        f"Wrote {len(artifact.documents)} documents and {len(artifact.cases)} query embeddings "
        f"to {args.output}"
    )


if __name__ == "__main__":
    main()
