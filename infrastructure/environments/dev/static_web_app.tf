resource "azurerm_static_web_app" "web" {
  count               = var.deploy_application_platform ? 1 : 0
  name                = "stapp-${local.name_prefix}-${var.instance_number}"
  resource_group_name = azurerm_resource_group.main.name
  location            = "eastus2"
  sku_tier            = "Free"
  sku_size            = "Free"
  tags                = local.common_tags
}
