output "resource_group_name" {
  description = "Resource group containing the Terraform state storage."
  value       = azurerm_resource_group.terraform_state.name
}

output "storage_account_name" {
  description = "Storage account used for remote Terraform state."
  value       = azurerm_storage_account.terraform_state.name
}

output "state_container_name" {
  description = "Blob container used for remote Terraform state."
  value       = azurerm_storage_container.terraform_state.name
}

output "primary_blob_endpoint" {
  description = "Primary Blob service endpoint."
  value       = azurerm_storage_account.terraform_state.primary_blob_endpoint
}
