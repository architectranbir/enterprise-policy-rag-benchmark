# Next Steps

## Current task

Extend evaluation coverage after the first secured fair vector-only benchmark.

## Immediate verification

1. Add a separate negative ACL, effective-date and refusal evaluation set.
2. Add configurable warm-up and repeated runs with median, p95 and confidence intervals.
3. Automate durable result upload from the private benchmark jobs instead of log reconstruction.
4. Run Terraform from a VNet-connected federated deployment identity, remove the operator IP
   exception, and verify private-only data-plane access.
5. Add repeatable integration tests for the local containerised backends.
6. Add CI workload identity federation and enforce the security posture with Azure Policy.
7. Decide whether global Qdrant read-only access is sufficient or implement collection-scoped
   JWT RBAC with a trusted token issuer and rotation lifecycle.

## Exact next implementation task

Implement the separate negative ACL, effective-date and refusal evaluation dataset and runner.

## Guardrails

- Use stable GA APIs and supported SDK releases only.
- Keep fair vector-only and platform-optimised benchmark modes separate.
- Use Microsoft Entra ID authentication; do not add service keys or secrets.
- Obtain user groups from trusted identity claims, never query text or user input.
- Preserve canonical chunks, metadata, ACLs and citation identifiers.
- Do not add hybrid or semantic ranking until vector-only retrieval is measured.
- Implement and verify one small component at a time.
