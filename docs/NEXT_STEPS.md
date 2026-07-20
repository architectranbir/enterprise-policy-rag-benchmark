# Next Steps

## Current task

Define the smallest Azure AI Search retrieval query contract and verify exact
metadata retrieval of the indexed synthetic chunk.

## Immediate verification

1. Create a feature branch from verified `main` at `83fa6ae` or later.
2. Define the minimal provider-neutral retrieval request and result contracts.
3. Implement only the Azure AI Search exact-metadata query path behind the agreed adapter.
4. Add focused unit tests for result mapping and failure handling.
5. Add a keyless live smoke test for the already indexed synthetic chunk.
6. Run the complete quality gate and live verification before publishing.

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
