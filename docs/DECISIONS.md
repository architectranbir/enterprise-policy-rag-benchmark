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

## ADR-009: Use managed identity, Key Vault references and private data planes

**Status:** Accepted
**Date:** 22 July 2026

The API and Qdrant Container Apps use separate user-assigned managed identities. Qdrant
administrator and read-only credentials are generated ephemerally, stored as write-only Key
Vault secret values and referenced from Container Apps with versionless secret URLs. The API
receives only the read-only credential and only when Qdrant is selected. The administrator key
is reserved for ingestion and administration.

Foundry, Search, Key Vault, ACR and Qdrant Azure Files storage use private endpoints, private
DNS and deny-by-default firewalls. A reviewed operator CIDR remains an explicit development
option; an empty allowlist produces private-only access. Anonymous blob access is disabled.

Application Insights local authentication is disabled. The API publishes telemetry using its
managed identity and a resource-scoped Monitoring Metrics Publisher assignment.

Azure Files is the documented exception to keyless access: the Container Apps environment
storage mount requires a storage account key. The key remains in infrastructure configuration,
is never injected into an application container and is rotated with the two-key procedure.

The stable `azure-monitor-opentelemetry` distribution currently depends on Microsoft-published
packages whose versions are labelled beta. Those exact bridge/exporter versions are pinned as
an unavoidable transitive compatibility exception; arbitrary prerelease packages remain
disallowed unless explicitly pinned and documented.

## ADR-010: Separate interactive identity, query and ingestion privileges

**Status:** Accepted
**Date:** 22 July 2026

The Web UI uses a dedicated Entra SPA registration and delegated `Policy.Read` scope. The API maps
only configured Entra security-group object IDs to canonical ACL groups. A separate ingestion
managed identity owns Search write permission, the PostgreSQL ingestion role and Qdrant's
administrator secret. The query API never receives ingestion credentials; Qdrant read access and
its secret-scoped Key Vault role exist only while Qdrant is the selected backend.

PostgreSQL role creation is a controlled one-time bootstrap operation. Its temporary Entra
administrator identity, job and ACR role are removed after the application and ingestion roles are
created. Extension installation remains an administrator responsibility rather than a runtime
store action.

## ADR-011: Freeze fair-vector dataset v1 before cloud re-ingestion

**Status:** Accepted
**Date:** 22 July 2026

Fair-vector dataset v1 contains eight synthetic policies across nine versions, producing 67
deterministic canonical chunks and 52 positive retrieval cases. Every relevance judgement points
to a real chunk that is effective on the case's `as_of` date and accessible to its synthetic user
groups. Version-sensitive cases deliberately distinguish the two travel-policy versions.

Negative ACL, expiry and unsupported-question cases remain in a separate evaluation track because
they test filtering and refusal behaviour rather than positive Recall@k or MRR. For a fair backend
comparison, chunk text, metadata and embeddings will be generated once into a versioned canonical
artifact. Azure AI Search, PostgreSQL/pgvector and Qdrant must ingest those exact vectors rather
than embedding independently.

## ADR-012: Use the Web UI as the only benchmark dashboard

**Status:** Accepted
**Date:** 22 July 2026

Power BI is removed from scope. No report, template, connector, embedding, documentation or
infrastructure for Power BI will be built. The Web application owns benchmark history,
comparisons, per-question evidence and exports.

## ADR-013: Keep three benchmark tracks and artifacts separate

**Status:** Accepted
**Date:** 22 July 2026

Fair vector-only, platform-optimised and enterprise-control evaluations are separate modes with
separate outputs. Controls score security and answer behaviour rather than contaminating positive
Recall@K. A mode guard prevents optimised runs from entering the fair comparison.

## ADR-014: Do not add LangGraph to a linear workflow

**Status:** Accepted
**Date:** 22 July 2026

The flow is embed, retrieve, generate, validate citations and return or refuse. It does not require
graph state or branching orchestration, so LangGraph is not implemented.
