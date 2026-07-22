resource "azurerm_key_vault" "application" {
  count                         = var.deploy_application_platform ? 1 : 0
  name                          = local.key_vault_name
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  tenant_id                     = var.tenant_id
  sku_name                      = "standard"
  rbac_authorization_enabled    = true
  purge_protection_enabled      = true
  soft_delete_retention_days    = 30
  public_network_access_enabled = local.restricted_public_access

  dynamic "network_acls" {
    for_each = var.enable_private_endpoints ? [1] : []
    content {
      bypass         = "AzureServices"
      default_action = "Deny"
      ip_rules       = var.operator_ip_ranges
    }
  }
  tags = local.common_tags
}

ephemeral "random_password" "qdrant_admin_api_key" {
  count   = var.deploy_application_platform ? 1 : 0
  length  = 48
  special = false
}

ephemeral "random_password" "qdrant_read_only_api_key" {
  count   = var.deploy_application_platform ? 1 : 0
  length  = 48
  special = false
}

resource "azurerm_key_vault_secret" "qdrant_admin_api_key" {
  count            = var.deploy_application_platform ? 1 : 0
  name             = "qdrant-admin-api-key"
  value_wo         = ephemeral.random_password.qdrant_admin_api_key[0].result
  value_wo_version = var.qdrant_secret_rotation_version
  key_vault_id     = azurerm_key_vault.application[0].id
  content_type     = "Qdrant administrator API key"
  tags             = local.common_tags
}

resource "azurerm_key_vault_secret" "qdrant_read_only_api_key" {
  count            = var.deploy_application_platform ? 1 : 0
  name             = "qdrant-read-only-api-key"
  value_wo         = ephemeral.random_password.qdrant_read_only_api_key[0].result
  value_wo_version = var.qdrant_secret_rotation_version
  key_vault_id     = azurerm_key_vault.application[0].id
  content_type     = "Qdrant query-only API key"
  tags             = local.common_tags
}
