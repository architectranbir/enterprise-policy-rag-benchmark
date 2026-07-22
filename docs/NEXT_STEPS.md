# Next Steps

## Current task

Expand and execute the fair vector-only benchmark after the secured live baseline.

## Immediate verification

1. Validate interactive Microsoft sign-in and `Policy.Read` consent in a normal user browser.
2. Expand the synthetic corpus and evaluation set before recording fair results.
3. Run repeatable fair vector-only evaluation across the populated backends and retain raw artifacts.
4. Run Terraform from a VNet-connected federated deployment identity, remove the operator IP
   exception, and verify private-only data-plane access.
5. Add repeatable integration tests for the local containerised backends.
6. Add CI workload identity federation and enforce the security posture with Azure Policy.
7. Decide whether global Qdrant read-only access is sufficient or implement collection-scoped
   JWT RBAC with a trusted token issuer and rotation lifecycle.

## Exact next implementation task

Use the deployed UI to complete interactive Microsoft consent, then run and capture the expanded
fair-vector evaluation without mixing it with platform-optimised results.

## Guardrails

- Use stable GA APIs and supported SDK releases only.
- Keep fair vector-only and platform-optimised benchmark modes separate.
- Use Microsoft Entra ID authentication; do not add service keys or secrets.
- Obtain user groups from trusted identity claims, never query text or user input.
- Preserve canonical chunks, metadata, ACLs and citation identifiers.
- Do not add hybrid or semantic ranking until vector-only retrieval is measured.
- Implement and verify one small component at a time.
