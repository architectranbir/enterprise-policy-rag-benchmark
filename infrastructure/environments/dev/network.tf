resource "azurerm_virtual_network" "application" {
  count               = var.deploy_application_platform ? 1 : 0
  name                = local.virtual_network_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.42.0.0/16"]
  tags                = local.common_tags
}

resource "azurerm_subnet" "container_apps" {
  count                = var.deploy_application_platform ? 1 : 0
  name                 = "snet-container-apps"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.application[0].name
  address_prefixes     = ["10.42.0.0/23"]

  delegation {
    name = "container-apps"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "postgresql" {
  count                = var.deploy_application_platform ? 1 : 0
  name                 = "snet-postgresql"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.application[0].name
  address_prefixes     = ["10.42.2.0/24"]
  service_endpoints    = ["Microsoft.Storage"]

  delegation {
    name = "postgresql"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "private_endpoints" {
  count                = var.deploy_application_platform && var.enable_private_endpoints ? 1 : 0
  name                 = "snet-private-endpoints"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.application[0].name
  address_prefixes     = ["10.42.3.0/24"]

  private_endpoint_network_policies = "Disabled"
}

resource "azurerm_private_dns_zone" "postgresql" {
  count               = var.deploy_application_platform ? 1 : 0
  name                = "private.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgresql" {
  count                 = var.deploy_application_platform ? 1 : 0
  name                  = "postgresql"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.postgresql[0].name
  virtual_network_id    = azurerm_virtual_network.application[0].id
}
