"""Production ASGI entry point with telemetry initialized before FastAPI imports."""

from policy_rag.config import Settings
from policy_rag.monitoring import configure_monitoring

settings = Settings()
configure_monitoring(settings)

# FastAPI must be imported after OpenTelemetry setup for automatic request instrumentation.
from policy_rag.api.app import create_configured_app  # noqa: E402

app = create_configured_app(settings)
