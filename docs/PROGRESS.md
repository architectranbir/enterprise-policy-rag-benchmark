# Progress

## Current phase

Phase 10 — multi-backend application foundation and local verification

## Completed and verified

- Provisioned the Terraform-managed Azure development foundation.
- Deployed Microsoft Foundry `text-embedding-3-large` with 3,072 dimensions.
- Provisioned keyless Azure AI Search and the canonical policy-chunk index.
- Added typed canonical policy, section, chunk and indexed-document models.
- Added deterministic ingestion, chunking and LlamaIndex node mapping.
- Added the provider-neutral embedding interface and keyless Foundry provider.
- Added the Azure AI Search schema and canonical document mapper.
- Added the typed Azure document-ingestion adapter through merged PR #14.
- Verified the complete gate on commit `c2b4d59`: Ruff passed, strict mypy passed and 82 tests passed.
- Added a keyless live ingestion smoke test on `feature/azure-search-ingestion-smoke-test`.
- Verified one synthetic chunk was embedded to 3,072 dimensions, uploaded to
  `policy-chunks-dev-v1` and read back with chunk ID
  `POL-HR-001:1.0:SEC-001:CHK-001`.
- Added provider-neutral retrieval request and result contracts.
- Added ACL-safe Azure AI Search exact-metadata filtering and retrieval.
- Verified live retrieval returned the indexed chunk for the `employees` group
  and returned zero results for the unauthorized `contractors` group.
- Verified the retrieval implementation with Ruff, strict mypy, 9 focused tests,
  the complete 91-test suite and a keyless live smoke test.
- Implemented Azure AI Search vector-only retrieval using `VectorizedQuery` with
  ACL, effective-date and metadata filters.
- Added the common vector-store interface, factory and `VECTOR_BACKEND` runtime switching.
- Added PostgreSQL/pgvector and Qdrant ingestion/retrieval adapters.
- Added query embedding, grounded generation, structured citations and deterministic refusal.
- Added FastAPI `/ask`, `/health` and `/ready`, correlation IDs and a minimal web UI.
- Added Docker Compose definitions, fair-vector evaluation models/dataset/metrics and CI.
- Extended optional Terraform definitions for Container Apps, Static Web Apps, ACR,
  PostgreSQL Flexible Server, Qdrant demo hosting, Key Vault and monitoring.
- Locally verified Ruff, strict mypy, 103 tests, an in-memory Qdrant ACL round trip,
  and both Terraform roots. Docker validation was unavailable because Docker is not installed.
- Added Microsoft Entra JWT signature/issuer/audience validation and fail-closed group-claim
  handling; insecure demo identity headers now require an explicit local-only setting.
- Migrated Foundry embedding and chat requests to the current GA `/openai/v1` contract,
  including deployment-as-model and `max_completion_tokens`.
- Pinned Azure AI Search clients to the `2025-09-01` GA data-plane API.
- Added a persistent Azure Files volume, API-key protection and filter payload indexes for
  the Qdrant demo, plus the PostgreSQL `VECTOR` extension allowlist configuration.
- Added Qdrant `1.18.2`, uv `0.11.16`, Terraform/AzureRM validation, Container App probes,
  ACR managed-identity pull configuration and a pinned `gpt-5.6-sol` deployment definition.
- Installed Docker/Compose/Colima, built the production image, and live-tested local
  PostgreSQL/pgvector and Qdrant ACL round trips.
- Deployed and live-tested GA `gpt-5.6-sol` grounded generation with a valid citation.
- Deployed ACR, VNet-integrated Container Apps, internal durable Qdrant, private PostgreSQL,
  Key Vault, monitoring and Static Web Apps. API `/health` and `/ready` are live and passing.
- Deployed the static UI files and verified the production homepage.
- Verified a final full Terraform refresh plan with no changes.

## Current branch

`feature/azure-search-vector-retrieval`

## Verified development resources

- Resource group: `rg-polrag-dev-uks-001`
- Managed identity: `id-polrag-dev-uks-001`
- Foundry resource: `aif-polrag-dev-uks-316e18`
- Foundry project: `proj-polrag-dev-001`
- Embedding deployment: `text-embedding-3-large`
- Azure AI Search: `srch-polrag-dev-uks-316e18`
- Search index: `policy-chunks-dev-v1`
- Region: `uksouth`

## Known limitations

- Platform-optimised hybrid and semantic retrieval are not implemented yet.
- Only one canonical chunk has been verified through live ingestion and retrieval.
- The deployed PostgreSQL Entra administrator exists, but a least-privilege application database
  role still requires a controlled bootstrap runner inside the VNet.
- The static UI Ask flow requires an Entra SPA/API app registration and consent before it can
  securely call the protected API; insecure demo identity remains disabled in Azure.
- The fair dataset is intentionally small and has not produced benchmark results.
- Public network access remains enabled for local development.
- Azure AI Search has one replica and one partition and is not configured for production availability.
- CI/CD workload identity federation and private endpoints for Search, Foundry, Key Vault and
  Storage are deferred; PostgreSQL is VNet-private and Qdrant ingress is internal.
