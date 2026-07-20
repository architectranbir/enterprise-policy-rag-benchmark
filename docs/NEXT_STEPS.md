# Next Steps

## Current task

Validate and publish the keyless Azure AI Search one-document ingestion smoke test.

## Immediate verification

1. Review the script and documentation diff for secrets and unrelated changes.
2. Run the locked Ruff formatting and lint checks.
3. Run strict mypy across `src`, `tests` and `scripts`.
4. Run the complete pytest suite.
5. Rerun the live smoke test and verify one uploaded document and 3,072 dimensions.
6. Commit, push, open a PR and merge it only when clean.

## Exact next implementation task

Define the smallest Azure AI Search retrieval query contract and add a keyless
smoke test that retrieves the indexed synthetic chunk by its exact canonical
metadata. Do not add hybrid or semantic ranking until the fair vector-only path
is implemented and measured.

## Guardrails

- Use stable GA APIs and supported SDK releases only.
- Keep fair vector-only and platform-optimised benchmark modes separate.
- Use Microsoft Entra ID authentication; do not add service keys or secrets.
- Preserve canonical chunks, metadata, ACLs and citation identifiers.
- Implement and verify one small component at a time.
