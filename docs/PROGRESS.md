# Progress

## Current phase

Phase 9 — Azure AI Search ingestion and retrieval

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

## Current branch

`feature/azure-search-ingestion-smoke-test`

## Latest merged base

`346f5e9` — Merge pull request #14 from
`architectranbir/feature/azure-search-ingestion`

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

- Azure AI Search retrieval query behaviour is not implemented yet.
- Only one canonical chunk has been verified through live ingestion.
- Public network access remains enabled for local development.
- Azure AI Search has one replica and one partition and is not configured for production availability.
- CI/CD workload identity federation and private networking are deferred.
