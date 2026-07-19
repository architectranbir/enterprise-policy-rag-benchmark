from importlib.util import find_spec


def test_policy_rag_package_is_discoverable() -> None:
    """Verify that the application package can be located."""
    assert find_spec("policy_rag") is not None
