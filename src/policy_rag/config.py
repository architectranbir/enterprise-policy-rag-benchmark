from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from policy_rag.retrieval.factory import VectorBackend


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    vector_backend: VectorBackend = VectorBackend.AZURE_AI_SEARCH
    azure_search_endpoint: str | None = None
    azure_search_index_name: str = "policy-chunks-dev-v1"
    azure_openai_endpoint: str = Field(default="", min_length=1)
    azure_openai_embedding_deployment: str = "text-embedding-3-large"
    azure_openai_chat_deployment: str = Field(default="", min_length=1)
    entra_tenant_id: str = Field(default="", min_length=1)
    entra_audience: str = Field(default="", min_length=1)
    allow_insecure_demo_identity: bool = False
    azure_client_id: str | None = None
    azure_monitor_enabled: bool = False
    applicationinsights_connection_string: SecretStr | None = None
    postgres_dsn: str = "postgresql://policy_rag:policy_rag@postgres:5432/policy_rag"
    postgres_use_entra: bool = False
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: SecretStr | None = None
    qdrant_collection: str = "policy_chunks"
