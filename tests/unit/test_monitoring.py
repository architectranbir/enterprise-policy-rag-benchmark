from typing import Any

import pytest
from pydantic import SecretStr

from policy_rag.config import Settings
from policy_rag.monitoring import configure_monitoring


def settings(**overrides: Any) -> Settings:
    return Settings(
        azure_openai_endpoint="https://foundry.example",
        azure_openai_chat_deployment="chat",
        entra_tenant_id="00000000-0000-0000-0000-000000000000",
        entra_audience="api://policy-rag-test",
        **overrides,
    )


def test_monitoring_is_noop_when_disabled() -> None:
    configure_monitoring(settings())


def test_monitoring_requires_connection_string_when_enabled() -> None:
    with pytest.raises(ValueError, match="APPLICATIONINSIGHTS_CONNECTION_STRING"):
        configure_monitoring(settings(azure_monitor_enabled=True, azure_client_id="client-id"))


def test_monitoring_requires_managed_identity_client_id() -> None:
    with pytest.raises(ValueError, match="AZURE_CLIENT_ID"):
        configure_monitoring(
            settings(
                azure_monitor_enabled=True,
                applicationinsights_connection_string=SecretStr("InstrumentationKey=test"),
            )
        )
