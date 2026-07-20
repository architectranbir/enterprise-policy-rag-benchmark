# Enterprise RAG Retrieval Benchmark — Repository Context

## Objective

Build a production-believable Enterprise Knowledge and Policy Intelligence RAG
application with three interchangeable retrieval backends:

1. Azure AI Search
2. PostgreSQL with pgvector
3. Qdrant

Only one backend is active during a normal request. Fair vector-only results and
platform-optimised results must be measured and reported separately.

## Current implementation

The repository currently contains:

- typed canonical policy, section and chunk models
- deterministic synthetic-policy loading, section extraction and chunking
- deterministic LlamaIndex node mapping
- a provider-neutral embedding contract and keyless Foundry embedding provider
- the Azure AI Search policy-chunk index contract
- canonical-to-Azure document mapping
- a typed Azure document-ingestion adapter
- keyless live smoke tests for Foundry embeddings, index creation and one-document ingestion
- Terraform-managed Azure development resources and RBAC

## Azure development architecture

- Microsoft Foundry resource and project using the current resource/project model
- `text-embedding-3-large` deployment with 3,072 dimensions
- Azure AI Search Basic service with local authentication disabled
- Microsoft Entra ID authentication for application and local smoke tests
- stable GA APIs and SDKs only

The application managed identity has Foundry inference and Azure Search document
indexing permissions. The local developer has the narrowly scoped Azure Search
roles required to create the development index and run document-ingestion smoke tests.

## Benchmark guardrails

- Keep corpus, chunks, metadata, embeddings, metric and `top_k` identical in fair mode.
- Keep backend-specific retrieval behaviour behind application-owned interfaces.
- Preserve document version, effective dates, ACL metadata and citation identifiers.
- Use only synthetic or permitted public data.
- Do not use secrets, client data, preview APIs or classic Foundry Hub resources.

## Current verified boundary

Azure AI Search can accept and return one canonical synthetic policy chunk through
the keyless ingestion adapter. Retrieval query behaviour is not implemented yet.
