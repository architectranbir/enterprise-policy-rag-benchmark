# Security

## Trust boundaries

The public Web UI calls the externally reachable API. The API validates Microsoft Entra access
tokens before building an ACL-aware retrieval request. Data services are reached from the
VNet-integrated Container Apps environment. Qdrant has internal-only ingress.

## Identity and credentials

| Consumer | Resource | Authentication | Permission boundary |
|---|---|---|---|
| Query API | Foundry, Search | User-assigned managed identity | Service data-plane RBAC |
| Query API | Application Insights | User-assigned managed identity | Monitoring Metrics Publisher |
| Query API, Qdrant backend only | Qdrant | Key Vault-backed read-only key | Read-only Qdrant API |
| Qdrant service | Key Vault | Dedicated user-assigned managed identity | Two secret-scoped reader roles |
| Qdrant ingestion/admin operation | Qdrant | Key Vault-backed administrator key | Administrative/write API |
| Container Apps environment | Azure Files | Storage account key | Mount infrastructure only; not injected into containers |
| Container Apps | ACR | User-assigned managed identity | AcrPull |

Qdrant keys are generated with Terraform ephemeral values and stored with the Key Vault
write-only argument. Secret values are not persisted in Terraform state. Container Apps uses
versionless Key Vault references so rotation can be adopted without committing a secret or
embedding it in Terraform configuration.

The open-source Qdrant deployment supports a global read-only key. Collection-scoped access
requires enabling Qdrant JWT RBAC and introducing a trusted token issuer and lifecycle. That is
not represented as complete by this repository; the query identity is read-only, not
collection-scoped.

## Network controls

When `enable_private_endpoints=true`, Terraform creates a dedicated private-endpoint subnet,
private DNS zones and endpoints for Foundry, Azure AI Search, Key Vault, ACR and the Qdrant
Azure Files service. Service firewalls default to deny. `operator_ip_ranges` is a reviewed
development escape hatch; use an empty set with a VNet-connected deployment runner for
private-only operation.

The storage account disables nested-item public access and local users. Shared-key access
cannot yet be disabled because Azure Container Apps Azure Files mounts require the account
key. The key is held in the Container Apps environment storage configuration and is not an
application environment variable.

## Rotation

### Qdrant keys

1. Increment `qdrant_secret_rotation_version` in protected environment configuration.
2. Review and apply the Terraform plan. It creates new Key Vault secret versions from ephemeral
   values.
3. Confirm Container Apps resolved the versionless references and restarted active revisions.
4. Verify Qdrant readiness and an authorised read/write smoke test from a trusted VNet runner.
5. Disable obsolete Key Vault secret versions after the rollout is verified.

### Azure Files keys

Never rotate the key currently used by the mount. Switch the environment storage configuration
to the secondary key, restart and verify Qdrant, rotate the primary key, switch back to the new
primary, restart and verify, then rotate the inactive secondary key. Commands and logs must not
print key values.

## Monitoring

Application Insights local authentication is disabled. The API configures the Azure Monitor
OpenTelemetry distribution with `ManagedIdentityCredential`, and the application identity has
the resource-scoped Monitoring Metrics Publisher role. The connection string identifies the
telemetry destination; Microsoft Entra authorisation is still required for ingestion.

## Remaining production controls

- Remove the development operator IP allowlist after a private CI/deployment runner or VPN is
  available.
- Validate the already-deployed Entra SPA/API consent flow in a normal user browser and document
  tenant-admin consent requirements for production tenants.
- Replace the single-node Qdrant demo topology with a supported highly available service for a
  production workload.
- If collection-scoped Qdrant access is required, design and validate JWT RBAC token issuance,
  expiry, rotation and collection claims.
- Add Azure Policy assignments, Defender recommendations and diagnostic alerting appropriate to
  the target subscription.
