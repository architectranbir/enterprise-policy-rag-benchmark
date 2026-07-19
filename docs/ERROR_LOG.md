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

