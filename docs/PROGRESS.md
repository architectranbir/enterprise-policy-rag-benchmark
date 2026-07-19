# Progress

## Current phase

Phase 4 — Controlled token-based chunking

## Completed and verified

- Added validated chunking configuration.
- Set the initial chunk-size baseline to 512 tokens.
- Set the initial overlap baseline to 128 tokens.
- Added tiktoken using the explicit `cl100k_base` encoding.
- Added an application-owned tokenizer wrapper.
- Added deterministic overlapping token-window creation.
- Updated section chunking to support multiple token-based chunks.
- Preserved deterministic chunk IDs and section-level citation metadata.
- Added unit tests for configuration, token counting, token windows and chunk creation.
- Added an integration test against the committed synthetic policy.
- Configured uv to reject prerelease dependencies by default.
- Completed the repository formatting, linting, strict type-checking and test quality gate.

## Current branch

`feature/controlled-chunking`

## Latest verified implementation commit

`0edbd6e`

## Current chunking baseline

- Maximum chunk size: 512 tokens
- Overlap: 128 tokens
- Token encoding: `cl100k_base`
- Section boundaries are preserved before token splitting.

## Not started

- LlamaIndex integration
- Canonical chunk-to-node conversion
- Embedding generation
- Retrieval adapters
- LangGraph workflow
- FastAPI service
- Terraform infrastructure
- Azure deployment
- Benchmark execution

## Known limitations

The current corpus contains one policy version.

The initial 512/128 configuration is a benchmark starting point and has not
yet been tuned using retrieval evaluation results.
