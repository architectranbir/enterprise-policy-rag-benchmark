# Progress

## Current phase

Phase 8 — Foundry embedding integration

## Completed and verified

- Merged the Terraform state bootstrap through PR #8.
- Created the Terraform development-environment root.
- Configured the development state in the shared Azure Blob backend.
- Defined shared resource naming, tags and validated environment variables.
- Provisioned the development resource group.
- Provisioned the user-assigned managed application identity.
- Provisioned the Microsoft Foundry resource.
- Provisioned the Microsoft Foundry project.
- Deployed `text-embedding-3-large`, model version `1`.
- Configured the embedding deployment with the `Standard` SKU, capacity `1` and `NoAutoUpgrade`.
- Provisioned Azure AI Search with the Basic SKU, one replica and one partition.
- Enabled the free semantic-search tier.
- Disabled local authentication on Azure AI Search.
- Granted the application identity `Cognitive Services OpenAI User` on the Foundry resource.
- Granted the application identity `Search Index Data Contributor` on Azure AI Search.
- Added Terraform outputs for application-facing resource names, endpoints and identity identifiers.
- Verified the embedding deployment provisioning state as `Succeeded`.
- Verified Azure AI Search as `Succeeded` and `running`.
- Verified Terraform configuration and deployed infrastructure have no drift.
- Added `azure-identity` for Microsoft Entra authentication.
- Added a keyless Foundry embedding smoke test using `DefaultAzureCredential` and the stable `2024-10-21` GA REST API.
- Verified live inference from `text-embedding-3-large` returned 3,072 dimensions and consumed 6 prompt tokens.

## Current branch

`feature/foundry-embedding-smoke-test`

## Latest verified base commit

`e4cc625`

The Azure development foundation was merged through PR #9. The current embedding smoke-test changes have not yet been committed.

## Verified development resources

- Resource group: `rg-polrag-dev-uks-001`
- Managed identity: `id-polrag-dev-uks-001`
- Foundry resource: `aif-polrag-dev-uks-316e18`
- Foundry project: `proj-polrag-dev-001`
- Embedding deployment: `text-embedding-3-large`
- Azure AI Search: `srch-polrag-dev-uks-316e18`
- Region: `uksouth`

## Remote state

- Backend: Azure Blob Storage
- Authentication: Microsoft Entra ID
- Backend values: ignored local configuration
- State locking: Azure Blob native locking
- Current Terraform plan: no drift

## Not started

- Provider-neutral embedding interface and production embedding integration
- Azure AI Search index schema and retrieval adapter
- PostgreSQL with pgvector infrastructure and retrieval adapter
- Qdrant infrastructure and retrieval adapter
- Cross-backend retrieval benchmark execution
- Application hosting and monitoring

## Known limitations

- Public network access is enabled on Foundry and Azure AI Search for local development.
- Azure AI Search currently has one replica and one partition and is not configured for production availability.
- The free semantic-search tier has usage limits.
- No hosted application currently uses the managed identity.
- The bootstrap storage account permits public network access for local development.
- The local developer Blob role assignment is managed through Azure CLI rather than Terraform.
- CI/CD workload identity federation and tighter network controls will be added later.
