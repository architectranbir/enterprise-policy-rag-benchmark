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

