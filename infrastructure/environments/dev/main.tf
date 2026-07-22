resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_user_assigned_identity" "application" {
  name                = local.managed_identity_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_user_assigned_identity" "qdrant" {
  count               = var.deploy_application_platform ? 1 : 0
  name                = "id-${local.name_prefix}-qdrant"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_user_assigned_identity" "ingestion" {
  count               = var.deploy_application_platform ? 1 : 0
  name                = "id-${local.name_prefix}-ingestion"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_user_assigned_identity" "postgres_bootstrap" {
  count               = var.deploy_application_platform && var.enable_postgres_bootstrap ? 1 : 0
  name                = "id-${local.name_prefix}-postgres-bootstrap"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}
