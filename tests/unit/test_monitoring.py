import pytest
from pydantic import SecretStr

from policy_rag.config import Settings
from policy_rag.monitoring import configure_monitoring


def test_monitoring_is_noop_when_disabled() -> None:
    configure_monitoring(Settings())


def test_monitoring_requires_connection_string_when_enabled() -> None:
    with pytest.raises(ValueError, match="APPLICATIONINSIGHTS_CONNECTION_STRING"):
        configure_monitoring(Settings(azure_monitor_enabled=True, azure_client_id="client-id"))


def test_monitoring_requires_managed_identity_client_id() -> None:
    with pytest.raises(ValueError, match="AZURE_CLIENT_ID"):
        configure_monitoring(
            Settings(
                azure_monitor_enabled=True,
                applicationinsights_connection_string=SecretStr("InstrumentationKey=test"),
            )
        )
