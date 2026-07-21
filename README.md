# Enterprise Policy RAG Benchmark

A production-believable policy assistant that compares Azure AI Search,
PostgreSQL/pgvector, and Qdrant behind one retrieval contract. Normal requests use
exactly one backend selected by `VECTOR_BACKEND`. Fair vector-only and future
platform-optimised measurements are kept separate.

## Local setup

Requirements: Python 3.13, `uv`, Terraform 1.15.7, and optionally Docker.

```bash
cp .env.example .env
uv sync --locked
uv run --locked pytest
```

Set the Azure Foundry endpoint and deployment names in `.env`. Authentication uses
`DefaultAzureCredential`; credentials and service keys must not be committed.

## Run

```bash
uv run --locked python scripts/ingest_corpus.py
uv run --locked uvicorn policy_rag.api.app:create_configured_app --factory --reload
```

The API exposes `POST /ask`, `GET /health`, and `GET /ready`. With Docker available,
`docker compose up --build` starts the API, UI, PostgreSQL/pgvector, and Qdrant; the
UI is served at `http://localhost:8080`.

`/ask` validates Microsoft Entra bearer tokens and obtains the user ID and groups only
from signed token claims. The bundled UI can use `X-Demo-User-*` headers only when
`ALLOW_INSECURE_DEMO_IDENTITY=true`; this flag must remain false in deployed environments.

## Quality gate

```bash
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy src tests scripts
uv run --locked pytest
terraform -chdir=infrastructure/bootstrap fmt -check -recursive
terraform -chdir=infrastructure/bootstrap validate
terraform -chdir=infrastructure/environments/dev fmt -check -recursive
terraform -chdir=infrastructure/environments/dev validate
```

The versioned fair evaluation dataset is in `data/evaluation`. Do not report results
until every backend has been populated from identical canonical chunks and the run
artifacts have been captured.
