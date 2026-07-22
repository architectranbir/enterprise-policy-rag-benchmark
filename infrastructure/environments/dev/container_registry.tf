resource "azurerm_container_registry" "application" {
  count                                 = var.deploy_application_platform ? 1 : 0
  name                                  = local.container_registry_name
  resource_group_name                   = azurerm_resource_group.main.name
  location                              = azurerm_resource_group.main.location
  sku                                   = var.enable_private_endpoints ? "Premium" : "Basic"
  admin_enabled                         = false
  public_network_access_enabled         = local.restricted_public_access
  network_rule_bypass_option            = "None"
  network_rule_bypass_for_tasks_enabled = false
  network_rule_set = var.enable_private_endpoints ? [{
    default_action = "Deny"
    ip_rule = [
      for cidr in var.operator_ip_ranges : {
        action   = "Allow"
        ip_range = cidr
      }
    ]
  }] : null
  tags = local.common_tags
}
