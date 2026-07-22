resource "azurerm_role_assignment" "application_search_data_reader" {
  scope                = azurerm_search_service.benchmark.id
  role_definition_name = "Search Index Data Reader"
  principal_id         = azurerm_user_assigned_identity.application.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "application_foundry_openai_user" {
  scope                = azurerm_cognitive_account.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_user_assigned_identity.application.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "application_acr_pull" {
  count                = var.deploy_application_platform ? 1 : 0
  scope                = azurerm_container_registry.application[0].id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.application.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "application_qdrant_read_only_secret_reader" {
  count                = var.deploy_application_platform && var.vector_backend == "qdrant" ? 1 : 0
  scope                = azurerm_key_vault_secret.qdrant_read_only_api_key[0].resource_versionless_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.application.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "qdrant_admin_secret_reader" {
  count                = var.deploy_application_platform ? 1 : 0
  scope                = azurerm_key_vault_secret.qdrant_admin_api_key[0].resource_versionless_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.qdrant[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "qdrant_read_only_secret_reader" {
  count                = var.deploy_application_platform ? 1 : 0
  scope                = azurerm_key_vault_secret.qdrant_read_only_api_key[0].resource_versionless_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.qdrant[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "application_monitoring_metrics_publisher" {
  count                = var.deploy_application_platform ? 1 : 0
  scope                = azurerm_application_insights.application[0].id
  role_definition_name = "Monitoring Metrics Publisher"
  principal_id         = azurerm_user_assigned_identity.application.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "ingestion_acr_pull" {
  count                = var.deploy_application_platform ? 1 : 0
  scope                = azurerm_container_registry.application[0].id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.ingestion[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "ingestion_foundry_openai_user" {
  count                = var.deploy_application_platform ? 1 : 0
  scope                = azurerm_cognitive_account.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_user_assigned_identity.ingestion[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "ingestion_search_data_contributor" {
  count                = var.deploy_application_platform ? 1 : 0
  scope                = azurerm_search_service.benchmark.id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = azurerm_user_assigned_identity.ingestion[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "ingestion_qdrant_admin_secret_reader" {
  count                = var.deploy_application_platform ? 1 : 0
  scope                = azurerm_key_vault_secret.qdrant_admin_api_key[0].resource_versionless_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.ingestion[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "postgres_bootstrap_acr_pull" {
  count                = var.deploy_application_platform && var.enable_postgres_bootstrap ? 1 : 0
  scope                = azurerm_container_registry.application[0].id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.postgres_bootstrap[0].principal_id
  principal_type       = "ServicePrincipal"
}
