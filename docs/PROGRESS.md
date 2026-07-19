# Progress

## Current phase

Phase 3 — Policy section extraction and chunk foundation

## Completed and verified

- Added the canonical `PolicySection` model.
- Added numbered Markdown section extraction.
- Preserved policy version, effective-date, classification and ACL metadata.
- Added the canonical `PolicyChunk` model.
- Added deterministic section-to-chunk conversion.
- Added unit tests for section and chunk validation.
- Added parser tests for numbered and nested sections.
- Added integration tests against the committed synthetic policy.
- Verified that the policy produces 11 sections and 11 baseline chunks.
- Ruff formatting and linting passed.
- mypy strict type checking passed.
- All current automated tests passed.

## Current branch

`feature/policy-sections-chunks`

## Latest verified implementation commit

`ec3498f`

## Current chunking baseline

Each logical policy section currently produces one deterministic retrieval chunk.

## Not started

- Long-section splitting
- LlamaIndex integration
- Embedding generation
- Retrieval adapters
- LangGraph workflow
- FastAPI service
- Terraform infrastructure
- Azure deployment
- Benchmark execution

## Known limitations

The current corpus contains one policy version.

The baseline does not yet split long sections according to token limits.
