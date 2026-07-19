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

