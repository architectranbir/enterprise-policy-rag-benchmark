# Next Steps

## Current task

Complete the two identity-dependent production handoff items.

## Immediate verification

1. Create/review the Entra SPA/API app registration, redirect URI and delegated scope, then wire
   MSAL into the deployed Web UI.
2. Run a one-time VNet-scoped PostgreSQL bootstrap identity/job to create the least-privilege
   application principal with `pgaadauth_create_principal`.
3. Ingest identical canonical chunks into all three deployed backends.
4. Expand the synthetic corpus and evaluation set before recording fair results.
5. Preserve the verified no-drift Terraform plan and review every future apply.
6. Add repeatable integration tests for the local containerised backends.
7. Add private endpoints for remaining Azure PaaS services and CI workload federation.

## Exact next implementation task

Obtain the reviewed Entra application registration details and run an authenticated `/ask`
request with a real application token containing the expected audience and group claims.

## Guardrails

- Use stable GA APIs and supported SDK releases only.
- Keep fair vector-only and platform-optimised benchmark modes separate.
- Use Microsoft Entra ID authentication; do not add service keys or secrets.
- Obtain user groups from trusted identity claims, never query text or user input.
- Preserve canonical chunks, metadata, ACLs and citation identifiers.
- Do not add hybrid or semantic ranking until vector-only retrieval is measured.
- Implement and verify one small component at a time.
