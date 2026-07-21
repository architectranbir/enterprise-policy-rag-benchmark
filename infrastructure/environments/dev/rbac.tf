resource "azurerm_role_assignment" "application_search_data_contributor" {
  scope                = azurerm_search_service.benchmark.id
  role_definition_name = "Search Index Data Contributor"
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
