# Error Log

No application or infrastructure errors have been recorded yet.

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
- **Related commit:** Not committed yet.
