locals {
  name_prefix = join(
    "-",
    [
      var.workload_name,
      var.environment,
      var.location_short,
    ]
  )

  resource_group_name        = "rg-${local.name_prefix}-${var.instance_number}"
  managed_identity_name      = "id-${local.name_prefix}-${var.instance_number}"
  foundry_account_name       = "aif-${local.name_prefix}-${var.unique_suffix}"
  foundry_project_name       = "proj-${var.workload_name}-${var.environment}-${var.instance_number}"
  search_service_name        = "srch-${local.name_prefix}-${var.unique_suffix}"
  container_registry_name    = "acr${var.workload_name}${var.environment}${var.unique_suffix}"
  container_environment_name = "cae-${local.name_prefix}-${var.instance_number}"
  key_vault_name             = "kv-${local.name_prefix}-${var.unique_suffix}"
  postgres_server_name       = "psql-${local.name_prefix}-${var.unique_suffix}"
  qdrant_storage_name        = "st${var.workload_name}${var.environment}${var.unique_suffix}"
  virtual_network_name       = "vnet-${local.name_prefix}-${var.instance_number}"
  postgres_private_dns_name  = "${local.postgres_server_name}.postgres.database.azure.com"

  common_tags = merge(
    var.tags,
    {
      region = var.location
    }
  )
}
