# Next Steps

## Current task

Live-run the enterprise-controls, repeated fair and platform-optimised benchmark tracks.

## Immediate verification

1. Review and deploy the new image only after explicit approval.
2. Re-ingest a dedicated Qdrant dense+sparse optimised collection and update the Azure semantic
   configuration through a reviewed deployment.
3. Execute repeated fair, enterprise-control and platform-optimised jobs and persist schema-valid
   JSON, CSV and Markdown artifacts in durable storage.
4. Run Terraform from a VNet-connected federated deployment identity, remove the operator IP
   exception, and verify private-only data-plane access.
5. Add repeatable integration tests for the local containerised backends.
6. Add CI workload identity federation and enforce the security posture with Azure Policy.
7. Decide whether global Qdrant read-only access is sufficient or implement collection-scoped
   JWT RBAC with a trusted token issuer and rotation lifecycle.

## Exact next implementation task

Review the complete local diff and gates, then obtain approval for live benchmark deployment and
execution. Do not publish new comparison claims until those runs complete.

## Guardrails

- Use stable GA APIs and supported SDK releases only.
- Keep fair vector-only and platform-optimised benchmark modes separate.
- Use Microsoft Entra ID authentication; do not add service keys or secrets.
- Obtain user groups from trusted identity claims, never query text or user input.
- Preserve canonical chunks, metadata, ACLs and citation identifiers.
- Never mix platform-optimised results with the fair-vector comparison.
- Implement and verify one small component at a time.
