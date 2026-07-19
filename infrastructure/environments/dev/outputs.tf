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

output "search_service_name" {
  description = "Name of the Azure AI Search service."
  value       = azurerm_search_service.benchmark.name
}

output "search_endpoint" {
  description = "Azure AI Search data-plane endpoint."
  value       = azurerm_search_service.benchmark.endpoint
}
