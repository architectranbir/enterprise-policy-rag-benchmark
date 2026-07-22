resource "azurerm_postgresql_flexible_server" "application" {
  count                 = var.deploy_application_platform ? 1 : 0
  name                  = local.postgres_server_name
  resource_group_name   = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  version               = "18"
  sku_name              = "B_Standard_B1ms"
  storage_mb            = 32768
  backup_retention_days = 7
  zone                  = "1"

  delegated_subnet_id           = azurerm_subnet.postgresql[0].id
  private_dns_zone_id           = azurerm_private_dns_zone.postgresql[0].id
  public_network_access_enabled = false

  authentication {
    active_directory_auth_enabled = true
    password_auth_enabled         = false
    tenant_id                     = var.tenant_id
  }

  tags = local.common_tags
}

resource "azurerm_postgresql_flexible_server_active_directory_administrator" "application" {
  count               = var.deploy_application_platform ? 1 : 0
  server_name         = azurerm_postgresql_flexible_server.application[0].name
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = var.tenant_id
  object_id           = var.postgres_entra_administrator_object_id
  principal_name      = var.postgres_entra_administrator_name
  principal_type      = "User"
}

resource "azurerm_postgresql_flexible_server_active_directory_administrator" "bootstrap" {
  count               = var.deploy_application_platform && var.enable_postgres_bootstrap ? 1 : 0
  server_name         = azurerm_postgresql_flexible_server.application[0].name
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = var.tenant_id
  object_id           = azurerm_user_assigned_identity.postgres_bootstrap[0].principal_id
  principal_name      = azurerm_user_assigned_identity.postgres_bootstrap[0].name
  principal_type      = "ServicePrincipal"
}

resource "azurerm_postgresql_flexible_server_database" "application" {
  count     = var.deploy_application_platform ? 1 : 0
  name      = "policy_rag"
  server_id = azurerm_postgresql_flexible_server.application[0].id
  collation = "en_US.utf8"
  charset   = "UTF8"

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_postgresql_flexible_server_configuration" "extensions" {
  count     = var.deploy_application_platform ? 1 : 0
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.application[0].id
  value     = "VECTOR"
}
