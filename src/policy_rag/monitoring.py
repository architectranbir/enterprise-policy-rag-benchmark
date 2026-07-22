"""Azure Monitor OpenTelemetry initialization for the production entry point."""

from azure.identity import ManagedIdentityCredential
from azure.monitor.opentelemetry import configure_azure_monitor

from policy_rag.config import Settings


def configure_monitoring(settings: Settings) -> None:
    """Configure authenticated telemetry before FastAPI is imported."""
    if not settings.azure_monitor_enabled:
        return
    if settings.applicationinsights_connection_string is None:
        raise ValueError(
            "APPLICATIONINSIGHTS_CONNECTION_STRING is required when Azure Monitor is enabled"
        )
    if not settings.azure_client_id:
        raise ValueError("AZURE_CLIENT_ID is required when Azure Monitor is enabled")

    credential = ManagedIdentityCredential(client_id=settings.azure_client_id)
    configure_azure_monitor(
        connection_string=settings.applicationinsights_connection_string.get_secret_value(),
        credential=credential,
        logger_name="policy_rag",
    )
