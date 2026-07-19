# Progress

## Current phase

Phase 2 — Synthetic policy corpus and source loading

## Completed and verified

- Created the first fictional enterprise policy: Remote Working Policy.
- Added machine-readable metadata and human-readable Markdown content.
- Validated corpus metadata against the canonical `PolicyDocument` model.
- Added `PolicySourceDocument` for validated metadata and source content.
- Added a source loader for individual policy versions.
- Added recursive corpus discovery with deterministic ordering.
- Added duplicate document-version protection.
- Added unit tests for valid and invalid source documents.
- Added unit tests for empty and duplicate corpus scenarios.
- Added an integration test against the committed synthetic corpus.
- Ruff formatting and linting passed.
- mypy strict type checking passed.
- All current automated tests passed.

## Current branch

`feature/synthetic-policy-corpus`

## Latest verified implementation commit

`05ab1c7`

## Not started

- Section extraction and chunk models
- LlamaIndex ingestion
- Embedding generation
- Retrieval adapters
- LangGraph workflow
- FastAPI service
- Terraform infrastructure
- Azure deployment
- Benchmark execution

## Known limitations

The corpus currently contains one policy version.

The loader validates and discovers source documents, but it does not yet split
documents into sections or chunks.
