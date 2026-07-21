# Architecture Decisions

## ADR-001: Use interchangeable retrieval backends

**Status:** Accepted
**Date:** 19 July 2026

### Context

The policy assistant needs to evaluate different retrieval approaches without changing the rest of the application.

The selected options represent three different platform models:

* Azure AI Search as a managed search service
* PostgreSQL with pgvector as a relational database with vector search
* Qdrant as a dedicated vector database

### Decision

The application will use a common retrieval interface with separate implementations for Azure AI Search, PostgreSQL with pgvector and Qdrant.

Only one retrieval backend will be active during a normal application run.

The active backend will be selected through application configuration.

### Reason

Keeping retrieval behind a common interface allows the document ingestion, question-answering workflow, API and evaluation logic to remain consistent.

It also allows each backend to be tested independently using the same documents, chunks, embeddings, metadata and evaluation questions.

### Consequences

* Backend-specific code must remain inside its retrieval adapter.
* The application must not query all three backends for a single user request.
* Controlled and platform-specific benchmark results must be reported separately.
* Adding another retrieval backend later will require a new adapter rather than changes throughout the application.

## ADR-002: Use LlamaIndex core for ingestion node mapping

**Status:** Accepted
**Date:** 19 July 2026

### Context

The application already owns the canonical policy, section and chunk models.
The benchmark requires identical chunks and metadata across Azure AI Search,
PostgreSQL with pgvector and Qdrant.

### Decision

Use `llama-index-core` to convert canonical `PolicyChunk` objects into
deterministic LlamaIndex `TextNode` objects.

LlamaIndex will support the ingestion layer. Retrieval will remain behind the
application-owned retrieval interface.

### Reason

This provides useful ingestion abstractions without hiding backend-specific
retrieval behaviour or changing the canonical chunk contract.

### Consequences

- Canonical chunk IDs remain the LlamaIndex node IDs.
- All retrieval backends receive the same node text and metadata.
- ACL, policy-version and citation metadata remain application-controlled.
- Embedding and retrieval integrations will be implemented separately.
- Only required LlamaIndex packages will be installed.

## ADR-003: Store Terraform state in Azure Blob Storage

**Status:** Accepted
**Date:** 19 July 2026

### Context

The Azure environment will be deployed from local development and later from
CI/CD. Terraform state must not depend on one developer's machine.

### Decision

Store Terraform state in a private Azure Blob container and authenticate through
Microsoft Entra ID.

Commit the reusable backend declaration, but keep account-specific backend
values in an ignored local configuration file.

### Reason

Azure Blob Storage provides central state storage, native locking and
consistency checking. Microsoft Entra ID avoids storing a storage-account key
in the repository or application configuration.

### Consequences

- Terraform operations use a shared remote state.
- Backend configuration must be initialized before plan or apply.
- Deployment identities require Blob data-plane access.
- State and local backend-value files must never be committed.
- CI/CD will later use workload identity federation rather than a developer login.


## ADR-004: Use the Microsoft Foundry resource and project model

**Status:** Accepted
**Date:** 20 July 2026

### Context

The benchmark requires a managed embedding-model deployment and a project
boundary for the Enterprise Knowledge and Policy Intelligence use case.

Microsoft Foundry supports projects as child resources of a project-enabled
Microsoft Cognitive Services account. The previous classic Foundry Hub model
does not represent the current architecture selected for this project.

### Decision

Provision the Microsoft Foundry resource with
`azurerm_cognitive_account` and enable project management.

Provision the Enterprise Knowledge and Policy Intelligence project with
`azurerm_cognitive_account_project`.

Manage both resources through the stable AzureRM provider.

Do not use classic Foundry Hub resources, preview APIs or private-preview
features.

### Reason

This is the current resource-and-project model supported by Microsoft Foundry
and the AzureRM provider.

It provides a clear parent resource for model deployments and an independently
named project boundary without introducing the older hub architecture.

### Consequences

- The Foundry resource owns model deployments and its inference endpoint.
- The Foundry project provides the project-level organizational boundary.
- Terraform records the resource and project as separate state objects.
- The application authenticates with Microsoft Entra ID.
- Application inference permission is granted at the Foundry-resource scope.
- Public network access remains enabled temporarily for local development.
- Private networking can be introduced later without changing the canonical
  policy or retrieval contracts.

## ADR-005: Keep generation and retrieval application-owned

**Status:** Accepted
**Date:** 22 July 2026

The application owns the retrieval, embedding, answer-generation, citation and
refusal contracts. Azure AI Search, Psycopg/pgvector and Qdrant are thin adapters.
This prevents backend SDK models from leaking into the API and preserves identical
fair-benchmark inputs. Grounded generation receives numbered retrieved evidence;
empty retrieval deterministically refuses before calling the generation model.

## ADR-006: Provision the application platform behind an explicit switch

**Status:** Accepted
**Date:** 22 July 2026

Container Apps, Static Web Apps, ACR, PostgreSQL Flexible Server, the Qdrant demo,
Key Vault and monitoring are declared in the development Terraform root behind
`deploy_application_platform`. The default remains false so adding the definitions
does not deploy or change live resources. Production applies require reviewed image
references, secrets supplied outside source control, cost review and explicit approval.

## ADR-007: Use current GA service contracts and fail-closed API identity

**Status:** Accepted
**Date:** 22 July 2026

The API validates Microsoft Entra access-token signatures, issuer, audience, expiry and group
claims before creating the retrieval access context. Group overage fails closed until a trusted
Graph-based resolver is implemented. Local demo headers are disabled by default. Foundry calls
use the GA `/openai/v1` endpoints, Azure AI Search is explicitly pinned to data-plane API
`2025-09-01`, and model/dependency versions remain pinned to stable supported releases.

## ADR-008: Keep Qdrant demo state durable and authenticated

**Status:** Accepted
**Date:** 22 July 2026

The single-replica Qdrant Container App mounts a dedicated Azure Files share, requires an API
key supplied outside source control, and remains internal-only. It is a benchmark/demo topology,
not a production highly available Qdrant cluster. Filter fields receive payload indexes so ACL
and effective-date filtering do not depend on unindexed scans.
