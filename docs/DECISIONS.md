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

