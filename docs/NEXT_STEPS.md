# Next Steps

## Current task

Review and commit the verified Azure development-foundation Terraform configuration and its documentation.

## Immediate verification before commit

1. Review the staged Terraform and documentation diff.
2. Confirm no ignored state, plan, provider or local configuration files are staged.
3. Run Terraform formatting and validation.
4. Run one final no-drift Terraform plan.

## After the Azure development foundation is committed

1. Add the smallest application-level keyless embedding smoke test.
2. Authenticate locally with `DefaultAzureCredential`.
3. Request one embedding from the deployed `text-embedding-3-large` model.
4. Verify that the returned vector contains 3,072 dimensions.
5. Define the provider-neutral embedding interface only after the smoke test succeeds.
6. Define the shared Azure AI Search index contract from the canonical `PolicyChunk` model.
7. Implement Azure AI Search ingestion and retrieval behind the application-owned interface.
8. Add PostgreSQL with pgvector and Qdrant separately, preserving identical chunks and metadata.

## Guardrails

- Use stable GA APIs and supported SDK releases only.
- Do not introduce classic Foundry Hub resources.
- Do not use public-preview or private-preview APIs.
- Keep canonical policy, section and chunk models application-owned.
- Keep backend-specific retrieval behaviour visible and independently measurable.
- Use Microsoft Entra ID authentication instead of application secrets or service keys.
- Implement and verify one small component at a time.
