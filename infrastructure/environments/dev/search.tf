resource "azurerm_search_service" "benchmark" {
  name                = local.search_service_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  sku             = "basic"
  replica_count   = 1
  partition_count = 1

  semantic_search_sku           = "free"
  local_authentication_enabled  = false
  public_network_access_enabled = true

  tags = local.common_tags
}
