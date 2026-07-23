# Enterprise Policy RAG Benchmark

[![CI](https://github.com/architectranbir/enterprise-policy-rag-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/architectranbir/enterprise-policy-rag-benchmark/actions/workflows/ci.yml)

[Live Web application](https://thankful-water-035fd740f.7.azurestaticapps.net/) ·
[Architecture](ARCHITECTURE.md) · [Security](docs/SECURITY.md) ·
[Benchmark evidence](benchmark_results/)

A production-believable policy assistant that compares Azure AI Search,
PostgreSQL/pgvector, and Qdrant behind one retrieval contract. Normal requests use
exactly one backend selected by `VECTOR_BACKEND`. Fair vector-only and platform-optimised
measurements are executed, validated and reported as separate tracks.

The Web UI contains the Policy Assistant and Benchmark Lab. The public application requires an
authorised Microsoft Entra identity for policy queries; benchmark evidence remains reproducible
from the repository. Power BI is intentionally out of scope.

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

Benchmark history is exposed by `GET /benchmarks/runs`, with raw evidence at
`GET /benchmarks/runs/{run_id}`. `POST /benchmarks/runs` fails closed until a secured server-side
benchmark job is configured. The UI never substitutes sample metrics for missing artifacts.

`/ask` validates Microsoft Entra bearer tokens, the delegated `Policy.Read` scope and mapped
security-group claims. The bundled Vite UI uses MSAL authorization code + PKCE and calls the API
with a bearer token. `X-Demo-User-*` headers exist only for explicit local development with
`ALLOW_INSECURE_DEMO_IDENTITY=true`; this flag remains false in Azure.

Azure ingestion runs as three manual Container Apps Jobs with a dedicated managed identity. Azure
AI Search uses RBAC, pgvector uses a least-privilege Entra database role, and only the Qdrant job
receives the Key Vault-backed administrator key. The normal API receives Qdrant's read-only key
only while `VECTOR_BACKEND=qdrant`.

## Quality gate

```bash
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy src tests scripts
uv run --locked pytest
uv run --locked python scripts/validate_benchmark_artifacts.py
terraform -chdir=infrastructure/bootstrap fmt -check -recursive
terraform -chdir=infrastructure/bootstrap validate
terraform -chdir=infrastructure/environments/dev fmt -check -recursive
terraform -chdir=infrastructure/environments/dev validate
cd web && npm ci && npm run lint && npm test && npm run build
```

The versioned fair evaluation dataset is in `data/evaluation`. Do not report results
until every backend has been populated from identical canonical chunks and the run
artifacts have been captured.

After validation, an authorised workload identity can durably publish immutable evidence with
`scripts/publish_benchmark_artifacts.sh <storage-account> <container> <run-id>`. It uses Microsoft
Entra `--auth-mode login`, never storage keys, and refuses to overwrite an existing run path.

Fair-vector dataset v1 contains 8 synthetic policies across 9 effective-dated versions,
67 deterministic canonical chunks and 52 positive retrieval cases. Integrity tests verify every
ground-truth chunk ID, ACL and effective date.

The deployed development indexes contain the same 67 pre-embedded canonical chunks. Each
retrieval track uses three warm-ups and three measured repetitions over 52 questions: 156 measured
retrievals per backend and 468 per track.

### Fair vector-only results

| Backend | Recall@5 | MRR | nDCG@5 | p50 | p95 |
|---|---:|---:|---:|---:|---:|
| Azure AI Search | 1.0000 | 0.9904 | 0.9929 | 32.57 ms | 45.33 ms |
| PostgreSQL/pgvector | 1.0000 | 0.9904 | 0.9929 | 94.44 ms | 121.03 ms |
| Qdrant | 1.0000 | 0.9904 | 0.9929 | 51.86 ms | 55.92 ms |

### Platform-optimised results

| Backend | Recall@5 | MRR | nDCG@5 | p50 | p95 |
|---|---:|---:|---:|---:|---:|
| Azure AI Search hybrid + semantic | 1.0000 | 1.0000 | 1.0000 | 75.69 ms | 181.34 ms |
| PostgreSQL FTS + vector fusion | 1.0000 | 0.9776 | 0.9833 | 95.54 ms | 117.43 ms |
| Qdrant dense + sparse RRF | 1.0000 | 0.9679 | 0.9763 | 55.87 ms | 60.04 ms |

### Enterprise controls

All three backends passed all eight synthetic control cases. ACL isolation, department/group
access, effective dates, policy-version selection, unsupported-question refusal, citation
correctness, groundedness and answer correctness each scored `1.0000` in this run. Per-case
evidence and phase-level embedding, retrieval, generation and end-to-end timings are published
under [`benchmark_results/enterprise-controls`](benchmark_results/enterprise-controls/).

### End-to-end RAG

All three backends passed all 12 representative questions. Citation correctness, groundedness and
answer correctness each scored `1.0000`. End-to-end p50 was 61.87 s for Azure AI Search, 61.59 s
for pgvector and 61.75 s for Qdrant. These generation latencies include development Foundry quota
retry/queue time and must not be interpreted as production serving latency.

Across the four isolated tracks, the published evidence contains exactly 996 measured executions:
468 fair retrievals, 468 platform-optimised retrievals, 24 enterprise-control cases and 36
end-to-end answers.

These development-scale measurements are workload-specific and do not establish a universal
winner. Retrieval latency excludes query embedding and answer generation. Complete raw rankings,
per-question metrics, control evidence and publish-ready comparisons are in
[`benchmark_results`](benchmark_results/).

For an existing Terraform-managed environment, build the Web UI from authoritative state outputs
instead of copying Entra IDs manually:

```bash
./scripts/build_web_from_terraform.sh
```
