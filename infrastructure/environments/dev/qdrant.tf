resource "azurerm_storage_account" "qdrant" {
  count                           = var.deploy_application_platform ? 1 : 0
  name                            = local.qdrant_storage_name
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  public_network_access_enabled   = local.restricted_public_access
  shared_access_key_enabled       = true
  allow_nested_items_to_be_public = false
  local_user_enabled              = false

  dynamic "network_rules" {
    for_each = var.enable_private_endpoints ? [1] : []
    content {
      default_action = "Deny"
      bypass         = ["AzureServices"]
      ip_rules       = local.single_ip_operator_rules
    }
  }
  tags = local.common_tags
}

resource "azurerm_storage_share" "qdrant" {
  count              = var.deploy_application_platform ? 1 : 0
  name               = "qdrant-data"
  storage_account_id = azurerm_storage_account.qdrant[0].id
  quota              = 5
}

resource "azurerm_container_app_environment_storage" "qdrant" {
  count                        = var.deploy_application_platform ? 1 : 0
  name                         = "qdrant-data"
  container_app_environment_id = azurerm_container_app_environment.application[0].id
  account_name                 = azurerm_storage_account.qdrant[0].name
  share_name                   = azurerm_storage_share.qdrant[0].name
  access_key                   = azurerm_storage_account.qdrant[0].primary_access_key
  access_mode                  = "ReadWrite"
}

resource "azurerm_container_app" "qdrant_demo" {
  count                        = var.deploy_application_platform ? 1 : 0
  name                         = "ca-${local.name_prefix}-qdrant"
  container_app_environment_id = azurerm_container_app_environment.application[0].id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.qdrant[0].id]
  }

  secret {
    name                = "admin-api-key"
    key_vault_secret_id = azurerm_key_vault_secret.qdrant_admin_api_key[0].versionless_id
    identity            = azurerm_user_assigned_identity.qdrant[0].id
  }

  secret {
    name                = "read-only-api-key"
    key_vault_secret_id = azurerm_key_vault_secret.qdrant_read_only_api_key[0].versionless_id
    identity            = azurerm_user_assigned_identity.qdrant[0].id
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "qdrant"
      image  = var.qdrant_container_image
      cpu    = 0.5
      memory = "1Gi"

      env {
        name        = "QDRANT__SERVICE__API_KEY"
        secret_name = "admin-api-key"
      }

      env {
        name        = "QDRANT__SERVICE__READ_ONLY_API_KEY"
        secret_name = "read-only-api-key"
      }

      volume_mounts {
        name = "qdrant-data"
        path = "/qdrant/storage"
      }
    }

    volume {
      name         = "qdrant-data"
      storage_name = azurerm_container_app_environment_storage.qdrant[0].name
      storage_type = "AzureFile"
    }
  }

  ingress {
    external_enabled = false
    target_port      = 6333
    transport        = "http"

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = local.common_tags

  depends_on = [
    azurerm_role_assignment.qdrant_admin_secret_reader,
    azurerm_role_assignment.qdrant_read_only_secret_reader,
  ]
}
