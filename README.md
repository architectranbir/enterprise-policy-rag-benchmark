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

## Security model

- Foundry and Azure AI Search use Microsoft Entra ID; local/key authentication is disabled.
- The deployed API uses a user-assigned managed identity for Azure access and telemetry.
- Qdrant administrator and read-only keys are generated as write-only Terraform values,
  stored in Key Vault, and consumed through versionless Container Apps Key Vault references.
- The query API receives only the Qdrant read-only key, and only when
  `VECTOR_BACKEND=qdrant`. The administrator key is reserved for Qdrant administration and
  ingestion operations.
- Foundry, Search, Key Vault, ACR and Qdrant file storage support private endpoints with
  private DNS. Set `operator_ip_ranges = []` for private-only data-plane access.
- Qdrant storage denies anonymous blob access. Azure Files currently requires a storage
  account key for the Container Apps environment mount; rotate it with the documented
  primary/secondary-key procedure and never expose it to an application container.
- Application Insights accepts Microsoft Entra-authenticated telemetry only; its local
  authentication is disabled.

See [Security](docs/SECURITY.md) for trust boundaries, credential ownership, rotation and
remaining production controls.

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
