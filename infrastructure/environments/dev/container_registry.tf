resource "azurerm_container_registry" "application" {
  count               = var.deploy_application_platform ? 1 : 0
  name                = local.container_registry_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = local.common_tags
}
