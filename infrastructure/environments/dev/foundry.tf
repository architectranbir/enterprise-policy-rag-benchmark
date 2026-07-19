resource "azurerm_cognitive_account" "foundry" {
  name                = local.foundry_account_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  kind     = "AIServices"
  sku_name = "S0"

  custom_subdomain_name      = local.foundry_account_name
  project_management_enabled = true

  local_auth_enabled            = false
  public_network_access_enabled = true

  identity {
    type = "SystemAssigned"
  }

  tags = local.common_tags
}

resource "azurerm_cognitive_account_project" "policy_intelligence" {
  name                 = local.foundry_project_name
  cognitive_account_id = azurerm_cognitive_account.foundry.id
  location             = azurerm_resource_group.main.location

  identity {
    type = "SystemAssigned"
  }
}
