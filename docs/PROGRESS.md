# Progress

## Current phase

Phase 5 — LlamaIndex node mapping

## Completed and verified

- Added the stable `llama-index-core` dependency.
- Added deterministic `PolicyChunk` to LlamaIndex `TextNode` mapping.
- Preserved canonical chunk IDs as node IDs.
- Added policy, version, date, classification, section and ACL metadata.
- Excluded operational metadata from embedding input.
- Excluded access-group metadata from LLM-visible metadata.
- Verified 11 deterministic nodes from the committed policy.
- Confirmed that embeddings are not generated in this phase.
- Added unit and integration tests.
- Added Python package boundaries for strict mypy checking.
- Ruff, mypy and all automated tests passed.

## Current branch

`feature/llamaindex-node-mapping`

## Latest verified implementation commit

`3492f7f`

## Current ingestion flow

Synthetic policy files → validated source → sections → token-based chunks → LlamaIndex TextNodes

## Not started

- Terraform remote-state bootstrap
- Microsoft Foundry resource and project
- Foundry embedding deployment
- Azure AI Search
- Embedding generation
- Retrieval adapters
- LangGraph workflow
- FastAPI service
- Azure deployment
- Benchmark execution

## Known limitations

The corpus currently contains one policy version.

The LlamaIndex nodes do not yet contain embeddings and have not been indexed
into a retrieval backend.
