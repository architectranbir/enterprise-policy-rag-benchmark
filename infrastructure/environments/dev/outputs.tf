output "resource_group_name" {
  description = "Name of the development resource group."
  value       = azurerm_resource_group.main.name
}

output "managed_identity_id" {
  description = "Azure resource ID of the application managed identity."
  value       = azurerm_user_assigned_identity.application.id
}

output "managed_identity_client_id" {
  description = "Client ID used by applications selecting the user-assigned managed identity."
  value       = azurerm_user_assigned_identity.application.client_id
}

output "managed_identity_principal_id" {
  description = "Microsoft Entra principal ID used for Azure RBAC assignments."
  value       = azurerm_user_assigned_identity.application.principal_id
}

output "foundry_endpoint" {
  description = "Microsoft Foundry resource endpoint used for model inference."
  value       = azurerm_cognitive_account.foundry.endpoint
}

output "foundry_project_name" {
  description = "Name of the Microsoft Foundry project."
  value       = azurerm_cognitive_account_project.policy_intelligence.name
}

output "embedding_deployment_name" {
  description = "Name of the embedding model deployment."
  value       = azurerm_cognitive_deployment.embedding.name
}

output "answer_deployment_name" {
  description = "Name of the grounded answer-generation model deployment."
  value       = try(azurerm_cognitive_deployment.answer[0].name, null)
}

output "search_service_name" {
  description = "Name of the Azure AI Search service."
  value       = azurerm_search_service.benchmark.name
}

output "search_endpoint" {
  description = "Azure AI Search data-plane endpoint."
  value       = azurerm_search_service.benchmark.endpoint
}

output "api_fqdn" {
  description = "Container Apps API hostname when the optional platform is enabled."
  value       = try(azurerm_container_app.api[0].ingress[0].fqdn, null)
}

output "static_web_app_hostname" {
  description = "Static Web App hostname when the optional platform is enabled."
  value       = try(azurerm_static_web_app.web[0].default_host_name, null)
}

output "entra_api_client_id" {
  description = "Public client ID of the protected API application registration."
  value       = try(azuread_application.api[0].client_id, null)
}

output "entra_web_client_id" {
  description = "Public client ID of the Web SPA application registration."
  value       = try(azuread_application.web[0].client_id, null)
}

output "entra_api_scope" {
  description = "Delegated scope requested by the Web SPA."
  value       = try("${one(azuread_application.api[0].identifier_uris)}/Policy.Read", null)
}
