resource "azurerm_log_analytics_workspace" "application" {
  count               = var.deploy_application_platform ? 1 : 0
  name                = "log-${local.name_prefix}-${var.instance_number}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

resource "azurerm_application_insights" "application" {
  count                        = var.deploy_application_platform ? 1 : 0
  name                         = "appi-${local.name_prefix}-${var.instance_number}"
  location                     = azurerm_resource_group.main.location
  resource_group_name          = azurerm_resource_group.main.name
  workspace_id                 = azurerm_log_analytics_workspace.application[0].id
  application_type             = "web"
  local_authentication_enabled = false
  tags                         = local.common_tags
}
