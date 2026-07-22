resource "azurerm_container_app_environment" "application" {
  count                      = var.deploy_application_platform ? 1 : 0
  name                       = local.container_environment_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.application[0].id
  infrastructure_subnet_id   = azurerm_subnet.container_apps[0].id
  tags                       = local.common_tags

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
    minimum_count         = 0
    maximum_count         = 0
  }
}

resource "azurerm_container_app" "api" {
  count                        = var.deploy_application_platform ? 1 : 0
  name                         = "ca-${local.name_prefix}-api"
  container_app_environment_id = azurerm_container_app_environment.application[0].id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.application.id]
  }

  registry {
    server   = azurerm_container_registry.application[0].login_server
    identity = azurerm_user_assigned_identity.application.id
  }

  dynamic "secret" {
    for_each = var.vector_backend == "qdrant" ? [1] : []
    content {
      name                = "qdrant-read-only-api-key"
      key_vault_secret_id = azurerm_key_vault_secret.qdrant_read_only_api_key[0].versionless_id
      identity            = azurerm_user_assigned_identity.application.id
    }
  }

  template {
    min_replicas = 1
    max_replicas = 3

    container {
      name   = "api"
      image  = var.api_container_image
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "VECTOR_BACKEND"
        value = var.vector_backend
      }

      env {
        name  = "AZURE_CLIENT_ID"
        value = azurerm_user_assigned_identity.application.client_id
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
        value = var.entra_audience
      }

      env {
        name  = "ALLOW_INSECURE_DEMO_IDENTITY"
        value = "false"
      }

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = azurerm_application_insights.application[0].connection_string
      }

      env {
        name  = "AZURE_MONITOR_ENABLED"
        value = "true"
      }

      env {
        name  = "APPLICATIONINSIGHTS_AUTHENTICATION_STRING"
        value = "Authorization=AAD;ClientId=${azurerm_user_assigned_identity.application.client_id}"
      }

      env {
        name  = "POSTGRES_DSN"
        value = "postgresql://${azurerm_user_assigned_identity.application.name}@${azurerm_postgresql_flexible_server.application[0].fqdn}:5432/policy_rag?sslmode=require"
      }

      env {
        name  = "POSTGRES_USE_ENTRA"
        value = "true"
      }

      env {
        name  = "QDRANT_URL"
        value = "https://${azurerm_container_app.qdrant_demo[0].ingress[0].fqdn}"
      }

      dynamic "env" {
        for_each = var.vector_backend == "qdrant" ? [1] : []
        content {
          name        = "QDRANT_API_KEY"
          secret_name = "qdrant-read-only-api-key"
        }
      }

      startup_probe {
        transport               = "HTTP"
        port                    = 8000
        path                    = "/health"
        interval_seconds        = 5
        timeout                 = 3
        failure_count_threshold = 12
      }

      liveness_probe {
        transport               = "HTTP"
        port                    = 8000
        path                    = "/health"
        interval_seconds        = 15
        timeout                 = 3
        failure_count_threshold = 3
      }

      readiness_probe {
        transport               = "HTTP"
        port                    = 8000
        path                    = "/ready"
        interval_seconds        = 10
        timeout                 = 5
        failure_count_threshold = 3
        success_count_threshold = 1
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = local.common_tags

  depends_on = [
    azurerm_role_assignment.application_acr_pull,
    azurerm_role_assignment.application_monitoring_metrics_publisher,
    azurerm_role_assignment.application_qdrant_read_only_secret_reader,
  ]
}
