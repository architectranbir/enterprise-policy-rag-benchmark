# Next Steps

## Current task

Align the embedding input with the canonical indexed chunk text, then implement
the fair Azure AI Search vector-only retrieval path.

## Immediate verification

1. Confirm ingestion embeds the same canonical text stored in the search index.
2. Add a regression test that prevents embedding/indexed-text divergence.
3. Extend the provider-neutral retrieval request for a query embedding.
4. Implement Azure AI Search vector-only retrieval with the existing ACL,
   effective-date and metadata filters.
5. Add focused unit tests and a keyless live vector-retrieval smoke test.
6. Run the complete quality gate before publishing.

## Exact next implementation task

Fix the ingestion text alignment before adding `VectorizedQuery`. Then retrieve
nearest policy chunks using the query embedding while preserving the existing
authorization and effective-date filters.

## Guardrails

- Use stable GA APIs and supported SDK releases only.
- Keep fair vector-only and platform-optimised benchmark modes separate.
- Use Microsoft Entra ID authentication; do not add service keys or secrets.
- Obtain user groups from trusted identity claims, never query text or user input.
- Preserve canonical chunks, metadata, ACLs and citation identifiers.
- Do not add hybrid or semantic ranking until vector-only retrieval is measured.
- Implement and verify one small component at a time.
