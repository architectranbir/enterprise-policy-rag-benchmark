locals {
  private_dns_zones = var.deploy_application_platform && var.enable_private_endpoints ? {
    search       = "privatelink.search.windows.net"
    cognitive    = "privatelink.cognitiveservices.azure.com"
    openai       = "privatelink.openai.azure.com"
    foundry      = "privatelink.services.ai.azure.com"
    key_vault    = "privatelink.vaultcore.azure.net"
    registry     = "privatelink.azurecr.io"
    storage_file = "privatelink.file.core.windows.net"
  } : {}
}

resource "azurerm_private_dns_zone" "application" {
  for_each            = local.private_dns_zones
  name                = each.value
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "application" {
  for_each              = local.private_dns_zones
  name                  = each.key
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.application[each.key].name
  virtual_network_id    = azurerm_virtual_network.application[0].id
  registration_enabled  = false
}

resource "azurerm_private_endpoint" "search" {
  count               = var.deploy_application_platform && var.enable_private_endpoints ? 1 : 0
  name                = "pe-${local.name_prefix}-search"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints[0].id
  tags                = local.common_tags

  private_service_connection {
    name                           = "search"
    private_connection_resource_id = azurerm_search_service.benchmark.id
    subresource_names              = ["searchService"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "search"
    private_dns_zone_ids = [azurerm_private_dns_zone.application["search"].id]
  }
}

resource "azurerm_private_endpoint" "foundry" {
  count               = var.deploy_application_platform && var.enable_private_endpoints ? 1 : 0
  name                = "pe-${local.name_prefix}-foundry"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints[0].id
  tags                = local.common_tags

  private_service_connection {
    name                           = "foundry"
    private_connection_resource_id = azurerm_cognitive_account.foundry.id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name = "foundry"
    private_dns_zone_ids = [
      azurerm_private_dns_zone.application["cognitive"].id,
      azurerm_private_dns_zone.application["openai"].id,
      azurerm_private_dns_zone.application["foundry"].id,
    ]
  }
}

resource "azurerm_private_endpoint" "key_vault" {
  count               = var.deploy_application_platform && var.enable_private_endpoints ? 1 : 0
  name                = "pe-${local.name_prefix}-key-vault"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints[0].id
  tags                = local.common_tags

  private_service_connection {
    name                           = "key-vault"
    private_connection_resource_id = azurerm_key_vault.application[0].id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "key-vault"
    private_dns_zone_ids = [azurerm_private_dns_zone.application["key_vault"].id]
  }
}

resource "azurerm_private_endpoint" "container_registry" {
  count               = var.deploy_application_platform && var.enable_private_endpoints ? 1 : 0
  name                = "pe-${local.name_prefix}-registry"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints[0].id
  tags                = local.common_tags

  private_service_connection {
    name                           = "registry"
    private_connection_resource_id = azurerm_container_registry.application[0].id
    subresource_names              = ["registry"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "registry"
    private_dns_zone_ids = [azurerm_private_dns_zone.application["registry"].id]
  }
}

resource "azurerm_private_endpoint" "qdrant_storage_file" {
  count               = var.deploy_application_platform && var.enable_private_endpoints ? 1 : 0
  name                = "pe-${local.name_prefix}-qdrant-file"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints[0].id
  tags                = local.common_tags

  private_service_connection {
    name                           = "qdrant-file"
    private_connection_resource_id = azurerm_storage_account.qdrant[0].id
    subresource_names              = ["file"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "qdrant-file"
    private_dns_zone_ids = [azurerm_private_dns_zone.application["storage_file"].id]
  }
}
