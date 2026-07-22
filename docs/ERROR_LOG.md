# Error Log

## Entry format

Each meaningful error should include:

* Date and time
* Component
* Branch and commit
* File path
* Command or request
* Exact error message
* Expected behaviour
* Root cause
* Fix applied
* Verification command and result
* Related commit

## ERR-001: Pytest collected no tests

- **Date and time:** 2026-07-19 18:36:04 IST
- **Component:** Python test foundation
- **Branch:** `feature/python-foundation`
- **File:** `tests/unit/test_package.py`
- **Command:** `uv run pytest`
- **Error:** `collected 0 items` and `no tests ran`
- **Expected behaviour:** One package-discovery test should be collected and executed.
- **Root cause:** The test file had been created but the test function had not been written and saved.
- **Fix:** Added `test_policy_rag_package_is_discoverable`.
- **Verification:** The targeted test passed, followed by successful Ruff, mypy and pytest checks with 1 passing test.
- **Related commit:** Not committed yet.

## ERR-002: Application package was not importable

- **Component:** Python packaging
- **Branch:** `feature/policy-domain-models`
- **Command:** `uv run python`
- **Error:** `ModuleNotFoundError: No module named 'policy_rag'`
- **Expected behaviour:** The application package should be importable during normal Python execution.
- **Root cause:** The project was created with `uv init --bare` and had no build system configured. The pytest-specific `pythonpath` setting did not apply to normal Python commands.
- **Fix:** Added the stable `uv_build` backend and configured `policy_rag` as the package module.
- **Verification:** `uv sync` installed the project and the policy model imported and instantiated successfully.
- **Related commit:** `d7c5c10`

## ERR-003: Quality gate found formatting issues

- **Component:** Python code quality
- **Branch:** `feature/synthetic-policy-corpus`
- **Command:** `uv run --locked ruff format --check .`
- **Error:** Ruff reported unformatted ingestion files and an unsorted import block.
- **Expected behaviour:** All source and test files should pass the configured formatting and linting checks.
- **Root cause:** Newly created files had not yet been processed by Ruff formatting and import organisation.
- **Fix:** Applied `ruff format` and the safe `ruff check --fix` import correction.
- **Verification:** The complete formatting, linting, type-checking and test quality gate passed.
- **Related commit:** `05ab1c7`

## ERR-004: uv prerelease policy mismatch

- **Date and time:** 2026-07-19 22:28:02 IST
- **Component:** Python dependency management
- **Branch:** `feature/controlled-chunking`
- **Command:** `uv run --locked python`
- **Error:** The lockfile needed an update because the prerelease mode differed between dependency resolution and command execution.
- **Expected behaviour:** Locked commands should run without attempting to modify `uv.lock`.
- **Root cause:** The dependency was added with the `disallow` prerelease strategy, while a later command used uv's default prerelease strategy.
- **Fix:** Added `prerelease = "disallow"` under `[tool.uv]`, regenerated the lockfile and verified the locked tokenizer command.
- **Verification:** tiktoken 0.13.0 loaded successfully with `cl100k_base`, and the complete quality gate passed.
- **Related commit:** `0edbd6e`



## ERR-005: mypy detected duplicate test modules

- **Date:** 2026-07-19
- **Component:** Python test package structure
- **Branch:** `feature/llamaindex-node-mapping`
- **Error:** Unit and integration test files with the same filename were treated as one module.
- **Root cause:** Test directories did not contain `__init__.py` package-boundary files.
- **Fix:** Added package boundaries under the unit and integration test directories.
- **Verification:** Strict mypy checking and the complete quality gate passed.
- **Related commit:** `3492f7f`

## ERR-006: Terraform version constraint blocked initialization

- **Date:** 2026-07-19
- **Component:** Terraform bootstrap
- **Branch:** `feature/terraform-state-bootstrap`
- **Error:** Terraform 1.15.7 did not satisfy the original minimum version constraint of 1.15.8.
- **Root cause:** The project constraint was narrower than the installed stable Terraform version.
- **Fix:** Changed the root-module constraint to `~> 1.15.7`, allowing compatible 1.15 patch releases while excluding 1.16 prereleases.
- **Verification:** Terraform initialization and configuration validation completed successfully.
- **Related commit:** `ca5904b`


## ERR-007: Remote backend configuration contained empty values

- **Date:** 2026-07-19
- **Component:** Terraform state migration
- **Branch:** `feature/terraform-state-bootstrap`
- **Error:** Backend initialization failed because the Blob container name was empty.
- **Root cause:** Terraform outputs were queried after the backend block had been introduced but before backend reinitialization, leaving the generated backend configuration empty.
- **Fix:** Read the deployed storage-account and container outputs from the existing local state and regenerated the ignored backend configuration.
- **Verification:** State migration completed, the remote Blob was verified and the no-drift plan succeeded.
- **Related commit:** `ca5904b`


## ERR-008: Terraform saved plan became stale

- **Date:** 2026-07-20
- **Component:** Terraform development-environment outputs
- **Branch:** `feature/azure-dev-foundation`
- **Command:** `terraform -chdir=infrastructure/environments/dev apply metadata-outputs.tfplan`
- **Error:** Terraform rejected the saved plan because the remote state had changed after the plan was created.
- **Expected behaviour:** The saved plan should apply only when it still matches the current Terraform state.
- **Root cause:** Another Terraform operation updated the shared remote state after `metadata-outputs.tfplan` was generated.
- **Fix:** Discarded the stale plan and ran a new Terraform plan against the current remote state.
- **Verification:** The new plan reported no changes, and `terraform output` returned the expected Foundry, embedding, Azure AI Search and managed-identity values.
- **Infrastructure impact:** None.

## ERR-009: OpenAI Python Azure client rejected Entra token provider

- **Date:** 2026-07-20
- **Component:** Microsoft Foundry embedding smoke test
- **Branch:** `feature/foundry-embedding-smoke-test`
- **Command:** `uv run --locked python scripts/smoke_test_foundry_embeddings.py`
- **Error:** `AzureOpenAI` raised `OpenAIError: Missing credentials` while an `azure_ad_token_provider` was supplied.
- **Expected behaviour:** The client should accept the documented Entra token provider and then submit the embedding request.
- **Root cause:** OpenAI Python 2.46.0 and 2.45.0 passed Azure credential validation but the base client rejected the internal API-key sentinel before making an Azure request.
- **Fix:** Replaced the SDK-specific smoke-test client with the stable `2024-10-21` GA REST endpoint using a Microsoft Entra bearer token. Removed the unused `openai` dependency and retained `azure-identity`.
- **Verification:** The SDK constructor failure is avoided by the REST implementation. The GA REST smoke test successfully generated an embedding from `text-embedding-3-large` with 3,072 dimensions and 6 prompt tokens.

## ERR-010: Local Azure AI Search document upload returned 403

- **Date and time:** 2026-07-20 14:10 IST
- **Component:** Azure AI Search document ingestion smoke test
- **Branch:** `feature/azure-search-ingestion-smoke-test`
- **Base commit:** `346f5e9`
- **File:** `scripts/smoke_test_azure_search_ingestion.py`
- **Command:** `uv run --locked python scripts/smoke_test_azure_search_ingestion.py`
- **Error:** `azure.core.exceptions.HttpResponseError: Operation returned an invalid status 'Forbidden'`
- **Expected behaviour:** The signed-in developer should upload and read back one synthetic policy chunk through Microsoft Entra ID.
- **Root cause:** The developer had `Search Service Contributor`, which permits index management but not document data-plane writes. Only the application managed identity had `Search Index Data Contributor`.
- **Fix:** With explicit approval, granted the signed-in developer `Search Index Data Contributor` at the single Azure AI Search service scope. Allowed time for Azure RBAC propagation before retrying.
- **Verification:** The live test uploaded one document, read back chunk `POL-HR-001:1.0:SEC-001:CHK-001` and verified a 3,072-dimensional embedding.
- **Related commit:** `0135157`

## ERR-011: Azure AI Search returned DateTimeOffset values as strings

- **Date:** 2026-07-20
- **Component:** Azure AI Search exact-metadata retrieval
- **Branch:** `feature/azure-search-retrieval`
- **Command:** `uv run --locked python scripts/smoke_test_azure_search_retrieval.py`
- **Error:** `ValueError: effective_from must be a date or datetime`
- **Expected behaviour:** The retrieval adapter should map Azure date values into the backend-neutral result model.
- **Root cause:** The adapter accepted Python `date` and `datetime` values, while the live Azure AI Search response returned `Edm.DateTimeOffset` as an ISO 8601 string such as `2026-01-01T00:00:00Z`.
- **Fix:** Extended the Azure result mapper to parse ISO 8601 date strings while retaining support for Python date and datetime values and rejecting invalid inputs.
- **Verification:** Nine focused retrieval tests passed, the full 91-test suite passed, and the live keyless smoke test returned one authorized result for `employees` and zero results for `contractors`.

## ERR-012: Baseline Ruff formatting drift

- **Date:** 2026-07-22
- **Component:** Existing Azure retrieval request model
- **Command:** `uv run --locked ruff format --check .`
- **Error:** `src/policy_rag/retrieval/models.py` would be reformatted.
- **Root cause:** The existing `query_embedding` field indentation was incomplete.
- **Fix:** Applied repository-standard Ruff formatting while completing vector retrieval.
- **Verification:** The final Ruff format and lint gates passed.

## ERR-013: Qdrant payload exposed ACL metadata to result validation

- **Date:** 2026-07-22
- **Component:** Qdrant retrieval adapter
- **Error:** `allowed_groups: Extra inputs are not permitted` in the neutral result model.
- **Root cause:** Qdrant returns filter-only ACL payload alongside citation fields.
- **Fix:** Remove `allowed_groups` before validating the backend-neutral result.
- **Verification:** The in-memory Qdrant authorised/denied ACL round-trip test passed.

## ERR-014: Docker executable unavailable

- **Date:** 2026-07-22
- **Component:** Local Docker Compose validation
- **Command:** `docker compose config --quiet`
- **Error:** `command not found: docker`
- **Impact:** Compose syntax and image builds are implemented but not locally verified.
- **Next action:** Install/start Docker and rerun configuration and build checks.

## ERR-015: Fresh pgvector initialization and 3,072-dimensional HNSW failed

- **Date:** 2026-07-22
- **Errors:** `vector type not found in the database`, followed by `column cannot have more than 2000 dimensions for hnsw index`.
- **Root cause:** Type registration preceded extension creation, and HNSW limits `vector` indexes to 2,000 dimensions.
- **Fix:** Bootstrap the extension before registration and use supported `halfvec(3072)` with `halfvec_cosine_ops`.
- **Verification:** Live PostgreSQL/pgvector and Qdrant authorised/denied ACL round trips passed.

## ERR-016: Container Apps rejected or failed the first API images

- **Date:** 2026-07-22
- **Errors:** Azure rejected `linux/arm64`; the next image raised `ModuleNotFoundError: policy_rag`.
- **Root cause:** Apple Silicon produced the wrong target architecture, then an editable environment referenced source absent from the final stage.
- **Fix:** Build `linux/amd64` with Buildx, pin base digests, and install with `uv sync --no-editable`.
- **Verification:** Local and deployed `/health` and `/ready` passed using immutable digest `sha256:63fffe7f54284e187bda7337112b5209311dc0696a6a152e28c7cf5d019730c9`.

## ERR-017: Initial Static Web Apps and PostgreSQL administrator operations failed

- **Date:** 2026-07-22
- **Errors:** West Europe rejected new Static Web Apps customers; the first PostgreSQL Entra administrator write returned an Azure internal error.
- **Fix:** Use provider-advertised East US 2. Retry the administrator after PostgreSQL reached `Ready`, then import it into Terraform state.
- **Verification:** Production UI homepage is live, the reviewed Entra administrator exists, and the final Terraform plan reports no changes.

## ERR-018: Key Vault rejected Terraform secret creation

- **Date:** 2026-07-22
- **Component:** Qdrant Key Vault migration
- **Error:** The signed-in operator lacked Key Vault secret data-plane permission.
- **Root cause:** Azure control-plane access does not grant secret write access when Key Vault RBAC is enabled.
- **Fix:** Temporarily assigned Key Vault Secrets Officer to the operator at the single vault scope for the migration. The application identities retain only secret-scoped reader roles.
- **Verification:** Terraform created separate write-only administrator and read-only secret versions and Container Apps resolved both versionless references. After the migration and final refresh plan, the temporary human role assignment was deleted and a scoped role query returned zero assignments.

## ERR-019: Azure services rejected single-host CIDR syntax

- **Date:** 2026-07-22
- **Component:** Foundry and Azure Storage firewalls
- **Error:** The services rejected an IPv4 address expressed with a `/32` suffix.
- **Root cause:** These resource APIs accept a single host as a plain address even though the project input is normalized as CIDR.
- **Fix:** Normalize `/32` operator entries to plain IP addresses only for service APIs requiring that representation.
- **Verification:** The deny-by-default firewall changes and private endpoints applied successfully.

## ERR-020: API readiness failed immediately after Search private endpoint creation

- **Date:** 2026-07-22
- **Component:** Container Apps DNS resolution
- **Error:** `/ready` failed after Azure AI Search was moved behind Private Link.
- **Root cause:** The running API revision retained the pre-Private-Link DNS result.
- **Fix:** Restarted the API revision after private DNS and endpoint provisioning completed.
- **Verification:** `/health` and `/ready` both returned HTTP 200 through the deployed endpoint.

## ERR-021: Docker did not discover the installed Buildx plugin

- **Date:** 2026-07-22
- **Component:** Production container build
- **Error:** Docker could not perform the required `linux/amd64` Buildx build from Apple Silicon.
- **Root cause:** The Homebrew Buildx plugin directory was not in Docker's plugin discovery path.
- **Fix:** Used a scoped temporary Docker configuration pointing at the installed plugin and the Colima socket.
- **Verification:** The image built as `linux/amd64`, passed a bootstrap smoke test, pushed to ACR and ran in the healthy API revision.

## ERR-022: Qdrant reports an Azure Files filesystem warning

- **Date:** 2026-07-22
- **Component:** Qdrant demo persistence
- **Warning:** Qdrant cannot guarantee data safety for the unrecognised mounted filesystem.
- **Impact:** The single-node Azure Files deployment is suitable only for this benchmark/demo and is not a production HA Qdrant topology.
- **Verification:** After both storage-key remounts Qdrant loaded its persisted Raft state, started REST and gRPC, and reported a ready container with zero restart failures.

## ERR-023: Foundry embedding ingestion was throttled

- **Date:** 2026-07-22
- **Error:** `HTTP 429 RateLimitReached`, with a 59-second retry interval.
- **Root cause:** The development deployment has 1 request per 10 seconds and 1,000 tokens per
  minute; ingestion made unbounded calls and did not honour `Retry-After`.
- **Fix:** Added bounded transient retries and quota-safe configurable embedding batches.
- **Verification:** Azure AI Search, pgvector and Qdrant each ingested 11 canonical chunks.

## ERR-024: pgvector ingestion attempted an administrator-only extension command

- **Date:** 2026-07-22
- **Error:** `InsufficientPrivilege: only members of azure_pg_admin are allowed to use CREATE EXTENSION vector`.
- **Root cause:** Runtime schema initialization repeated `CREATE EXTENSION` after the controlled
  administrator bootstrap had already installed it.
- **Fix:** Kept extension installation in the one-time bootstrap and limited runtime initialization
  to tables and indexes. Local Compose installs the extension through an init SQL mount.
- **Verification:** The managed-identity pgvector job ingested 11 chunks and the read-only API
  returned a grounded answer with the expected citation.

## ERR-025: Qdrant client used the wrong internal ingress port and timed out

- **Date:** 2026-07-22
- **Errors:** `httpx.ConnectTimeout`, followed by a 5-second payload-index `ReadTimeout`.
- **Root cause:** `QdrantClient` appends its default REST port 6333 when an HTTPS URL omits a port,
  while Container Apps terminates HTTPS on 443. Azure Files-backed index creation also exceeded the
  client's default read timeout.
- **Fix:** Set the internal Qdrant URL to explicit `:443` and added a typed configurable 60-second
  client timeout.
- **Verification:** The standard Qdrant ingestion job succeeded and the API, using only the
  read-only Key Vault credential, returned the expected grounded answer and citation.

## ERR-026: Query API retained an Azure AI Search write role

- **Date:** 2026-07-22
- **Component:** Azure AI Search RBAC
- **Issue:** The query API still held `Search Index Data Contributor` after ingestion moved to a
  separate managed identity.
- **Root cause:** The original combined runtime identity needed document-write access before the
  ingestion/query responsibility split.
- **Fix:** Replaced the query API assignment with `Search Index Data Reader`; only the ingestion
  identity retains `Search Index Data Contributor`.
- **Verification:** The scoped Terraform apply completed with one role added and one removed, and
  the deployed Azure AI Search readiness check remained successful.

## ERR-027: MSAL blocked nested authentication popups

- **Date:** 2026-07-22
- **Component:** Web UI authentication
- **Error:** `block_nested_popups`
- **Root cause:** The SPA used MSAL popup APIs while the UI itself was open in a popup-style browser
  surface, so MSAL correctly refused to open a second nested popup.
- **Fix:** Replaced login, interactive token acquisition and logout popups with MSAL redirect APIs;
  retained `handleRedirectPromise()` and aligned the redirect URI exactly with the registered root.
- **Verification:** The production Vite build passed, npm reported zero vulnerabilities, and Azure
  Static Web Apps CLI confirmed the production deployment. Interactive sign-in remains pending
  user confirmation because automated browser access is blocked by enterprise network policy.

## ERR-028: Web deployment used the Azure CLI client ID as the tenant ID

- **Date:** 2026-07-22
- **Component:** Web UI deployment configuration
- **Error:** `AADSTS90002: Tenant '04b07795-8ddb-461a-bbee-02f9e1bf7b46' not found.`
- **Root cause:** The AzureAD client-config composite state ID was parsed manually and its Azure CLI
  client ID segment was mistaken for the directory tenant ID.
- **Fix:** Rebuilt and deployed the SPA with the Azure-verified tenant
  `f674bff7-64c3-490b-a170-764ee5ade42d`. Added a Terraform tenant output and a state-driven Web
  build script so all public deployment settings come from authoritative outputs.
- **Verification:** Azure CLI and the ignored environment tfvars report the same tenant; the
  production bundle contains that tenant and excludes the incorrect ID; Vite build and npm audit
  passed; Static Web Apps CLI confirmed the production deployment.

## ERR-029: Monitoring unit tests depended on a developer `.env`

- **Date:** 2026-07-22
- **Component:** GitHub Actions quality gate
- **Error:** Three monitoring tests failed while constructing `Settings`; the remaining 117 tests
  passed.
- **Root cause:** The tests relied on required Foundry and Entra values from the ignored local
  `.env`, which is correctly absent on clean CI runners.
- **Fix:** Added explicit synthetic required settings to the monitoring-test fixture while retaining
  strict production configuration validation.
- **Verification:** Ruff formatting/lint, strict mypy and the exact pytest-with-coverage CI command
  passed locally with all 120 tests. PR and post-merge `main` CI both passed.

## ERR-030: Entra signing-key discovery used an invalid URL

- **Date:** 2026-07-22
- **Component:** API bearer-token validation
- **Error:** A correctly authenticated Web user received `bearer token validation failed`.
- **Root cause:** The validator appended `/discovery/v2.0/keys` to an issuer already ending in
  `/v2.0`, producing an invalid JWKS URL. Tenant, audience, delegated scope and group mapping were
  independently verified as correct.
- **Fix:** Use the tenant-specific Microsoft Entra JWKS endpoint published by the v2 OpenID metadata
  document and protect it with a focused construction test.
- **Verification:** The focused 12-test auth suite and complete quality gate passed with 121 tests;
  the immutable `linux/amd64` image was pushed and deployed; `/health` and `/ready` passed; and the
  final Terraform plan reported no changes. The user subsequently confirmed the signed-in Web flow
  returned a grounded Azure AI Search answer with the expected policy citation.

## ERR-031: Expanded-corpus integration test had formatting drift

- **Date:** 2026-07-22
- **Component:** Fair-vector benchmark dataset validation
- **Error:** Ruff's format check reported one unformatted integration-test file during the first
  complete quality run.
- **Root cause:** The new multi-version corpus assertion did not match the repository formatter's
  wrapping.
- **Fix:** Applied the pinned Ruff formatter to the affected test.
- **Verification:** The subsequent fail-fast quality gate passed Ruff formatting and lint, strict
  mypy and pytest with coverage: 122 tests passed with one expected local Qdrant payload-index
  warning.

## ERR-032: Container Apps execution override dropped inherited settings

- **Date:** 2026-07-22
- **Component:** Fair-vector ingestion jobs
- **Error:** All first artifact-ingestion executions failed `Settings` validation because required
  environment values were empty.
- **Root cause:** Starting a job with an image/command execution override replaced the container
  execution definition instead of inheriting its environment block.
- **Fix:** Updated the existing job templates while preserving their managed identity, environment
  and Qdrant Key Vault secret reference, then started normal executions.
- **Verification:** All three corrected jobs succeeded and Log Analytics recorded 67 pre-embedded
  chunks ingested by each backend.

## ERR-033: Non-root benchmark jobs could not persist under `/app`

- **Date:** 2026-07-22
- **Component:** Fair-vector benchmark result capture
- **Error:** Retrieval completed, then each job raised `PermissionError` while creating
  `/app/benchmark_results` as the non-root application user.
- **Root cause:** Log-emission mode still attempted the local-development default file write.
- **Fix:** Made disk output optional in log-emission mode and encoded complete raw runs as
  deterministic gzip/base64 numbered records below the Log Analytics line-size limit.
- **Verification:** Final benchmark executions succeeded for all three backends; numbered records
  reconstructed into three schema-valid 52-case raw JSON files with identical artifact and source
  hashes.

## ERR-034: Legacy Docker builder could not complete the cross-platform image

- **Date:** 2026-07-22
- **Component:** Benchmark container build
- **Error:** The legacy builder failed the multi-stage `linux/amd64` build on the ARM64 host because
  an intermediate image did not provide the requested platform.
- **Root cause:** Homebrew buildx was installed but not discovered as a Docker CLI plugin.
- **Fix:** Invoked the installed stable buildx binary directly with BuildKit.
- **Verification:** The final immutable benchmark image was pushed at manifest digest
  `sha256:fcfdb50f573629994ed41ee8c10379f629171e768bf21ee7ee447f55761f9c1d`, and all three final
benchmark executions succeeded from that image.

## ERR-035: Local validation tools were hidden by sandbox/plugin discovery

- **Date:** 2026-07-22
- **Component:** Local Terraform and Docker verification
- **Errors:** Terraform providers could not execute inside the filesystem sandbox; the Docker CLI
  did not discover the installed Compose plugin.
- **Fix:** Ran read-only Terraform validation with scoped approval and used the installed standalone
  `docker-compose` executable. No plan, apply, deployment or remote mutation was performed.
- **Verification:** Both Terraform roots validated successfully; Compose configuration passed and
  both API and Web images built successfully.
