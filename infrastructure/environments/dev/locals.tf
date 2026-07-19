locals {
  name_prefix = join(
    "-",
    [
      var.workload_name,
      var.environment,
      var.location_short,
    ]
  )

  resource_group_name   = "rg-${local.name_prefix}-${var.instance_number}"
  managed_identity_name = "id-${local.name_prefix}-${var.instance_number}"
  foundry_account_name  = "aif-${local.name_prefix}-${var.unique_suffix}"
  foundry_project_name  = "proj-${var.workload_name}-${var.environment}-${var.instance_number}"
  search_service_name   = "srch-${local.name_prefix}-${var.unique_suffix}"

  common_tags = merge(
    var.tags,
    {
      region = var.location
    }
  )
}
