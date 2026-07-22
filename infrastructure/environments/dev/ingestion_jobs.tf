locals {
  ingestion_jobs = var.deploy_application_platform ? {
    azure-search = { backend = "azure_ai_search", name_suffix = "ingest-ais" }
    pgvector     = { backend = "pgvector", name_suffix = "ingest-pgv" }
    qdrant       = { backend = "qdrant", name_suffix = "ingest-qdrant" }
  } : {}
}

resource "azurerm_container_app_job" "ingestion" {
  for_each                     = local.ingestion_jobs
  name                         = "ca-${local.name_prefix}-${each.value.name_suffix}"
  location                     = azurerm_resource_group.main.location
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.application[0].id
  workload_profile_name        = "Consumption"
  replica_timeout_in_seconds   = 1800
  replica_retry_limit          = 1

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.ingestion[0].id]
  }

  registry {
    server   = azurerm_container_registry.application[0].login_server
    identity = azurerm_user_assigned_identity.ingestion[0].id
  }

  dynamic "secret" {
    for_each = each.value.backend == "qdrant" ? [1] : []
    content {
      name                = "qdrant-admin-api-key"
      key_vault_secret_id = azurerm_key_vault_secret.qdrant_admin_api_key[0].versionless_id
      identity            = azurerm_user_assigned_identity.ingestion[0].id
    }
  }

  manual_trigger_config {
    parallelism              = 1
    replica_completion_count = 1
  }

  template {
    container {
      name    = "ingest"
      image   = var.api_container_image
      cpu     = 1
      memory  = "2Gi"
      command = ["python", "scripts/ingest_fair_artifact.py"]

      env {
        name  = "VECTOR_BACKEND"
        value = each.value.backend
      }
      env {
        name  = "AZURE_CLIENT_ID"
        value = azurerm_user_assigned_identity.ingestion[0].client_id
      }
      env {
        name  = "AZURE_SEARCH_ENDPOINT"
        value = azurerm_search_service.benchmark.endpoint
      }
      env {
        name  = "AZURE_SEARCH_INDEX_NAME"
        value = "policy-chunks-dev-v1"
      }
      env {
        name  = "AZURE_OPENAI_ENDPOINT"
        value = azurerm_cognitive_account.foundry.endpoint
      }
      env {
        name  = "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        value = azurerm_cognitive_deployment.embedding.name
      }
      env {
        name  = "AZURE_OPENAI_CHAT_DEPLOYMENT"
        value = azurerm_cognitive_deployment.answer[0].name
      }
      env {
        name  = "ENTRA_TENANT_ID"
        value = var.tenant_id
      }
      env {
        name  = "ENTRA_AUDIENCE"
        value = azuread_application.api[0].client_id
      }
      env {
        name  = "POSTGRES_DSN"
        value = "postgresql://${azurerm_user_assigned_identity.ingestion[0].name}@${azurerm_postgresql_flexible_server.application[0].fqdn}:5432/policy_rag?sslmode=require"
      }
      env {
        name  = "POSTGRES_USE_ENTRA"
        value = "true"
      }
      env {
        name  = "QDRANT_URL"
        value = "https://${azurerm_container_app.qdrant_demo[0].ingress[0].fqdn}:443"
      }

      dynamic "env" {
        for_each = each.value.backend == "qdrant" ? [1] : []
        content {
          name        = "QDRANT_API_KEY"
          secret_name = "qdrant-admin-api-key"
        }
      }
    }
  }

  tags = local.common_tags

  depends_on = [
    azurerm_role_assignment.ingestion_acr_pull,
    azurerm_role_assignment.ingestion_foundry_openai_user,
    azurerm_role_assignment.ingestion_search_data_contributor,
    azurerm_role_assignment.ingestion_qdrant_admin_secret_reader,
  ]
}

resource "azurerm_container_app_job" "postgres_bootstrap" {
  count                        = var.deploy_application_platform && var.enable_postgres_bootstrap ? 1 : 0
  name                         = "ca-${local.name_prefix}-pg-bootstrap"
  location                     = azurerm_resource_group.main.location
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.application[0].id
  workload_profile_name        = "Consumption"
  replica_timeout_in_seconds   = 600
  replica_retry_limit          = 0

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.postgres_bootstrap[0].id]
  }

  registry {
    server   = azurerm_container_registry.application[0].login_server
    identity = azurerm_user_assigned_identity.postgres_bootstrap[0].id
  }

  manual_trigger_config {
    parallelism              = 1
    replica_completion_count = 1
  }

  template {
    container {
      name    = "bootstrap"
      image   = var.api_container_image
      cpu     = 0.5
      memory  = "1Gi"
      command = ["python", "scripts/bootstrap_postgres_roles.py"]

      env {
        name  = "AZURE_CLIENT_ID"
        value = azurerm_user_assigned_identity.postgres_bootstrap[0].client_id
      }
      env {
        name  = "POSTGRES_ADMIN_DSN"
        value = "postgresql://${azurerm_user_assigned_identity.postgres_bootstrap[0].name}@${azurerm_postgresql_flexible_server.application[0].fqdn}:5432/postgres?sslmode=require"
      }
      env {
        name  = "POSTGRES_APPLICATION_DSN"
        value = "postgresql://${azurerm_user_assigned_identity.postgres_bootstrap[0].name}@${azurerm_postgresql_flexible_server.application[0].fqdn}:5432/policy_rag?sslmode=require"
      }
      env {
        name  = "APPLICATION_PRINCIPAL_NAME"
        value = azurerm_user_assigned_identity.application.name
      }
      env {
        name  = "APPLICATION_PRINCIPAL_OBJECT_ID"
        value = azurerm_user_assigned_identity.application.principal_id
      }
      env {
        name  = "INGESTION_PRINCIPAL_NAME"
        value = azurerm_user_assigned_identity.ingestion[0].name
      }
      env {
        name  = "INGESTION_PRINCIPAL_OBJECT_ID"
        value = azurerm_user_assigned_identity.ingestion[0].principal_id
      }
    }
  }

  tags = local.common_tags

  depends_on = [
    azurerm_postgresql_flexible_server_active_directory_administrator.bootstrap,
    azurerm_role_assignment.postgres_bootstrap_acr_pull,
  ]
}
