variable "subscription_id" {
  description = "Azure subscription ID used for the Terraform state resources."
  type        = string
  nullable    = false

  validation {
    condition = can(
      regex(
        "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        var.subscription_id
      )
    )
    error_message = "subscription_id must be a valid Azure subscription GUID."
  }
}

variable "location" {
  description = "Azure region for the Terraform state resources."
  type        = string
  default     = "uksouth"
  nullable    = false

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must not be empty."
  }
}

variable "resource_group_name" {
  description = "Resource group that contains the Terraform state storage account."
  type        = string
  default     = "rg-polrag-tfstate-uks-001"
  nullable    = false

  validation {
    condition = (
      length(var.resource_group_name) >= 1 &&
      length(var.resource_group_name) <= 90
    )
    error_message = "resource_group_name must contain between 1 and 90 characters."
  }
}

variable "storage_account_name" {
  description = "Globally unique storage account name for Terraform state."
  type        = string
  nullable    = false

  validation {
    condition = can(
      regex(
        "^[a-z0-9]{3,24}$",
        var.storage_account_name
      )
    )
    error_message = "storage_account_name must contain 3 to 24 lowercase letters or numbers only."
  }
}

variable "state_container_name" {
  description = "Private blob container used to store Terraform state."
  type        = string
  default     = "tfstate"
  nullable    = false

  validation {
    condition = can(
      regex(
        "^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?$",
        var.state_container_name
      )
    )
    error_message = "state_container_name must be a valid lowercase Azure blob-container name."
  }
}

variable "tags" {
  description = "Tags applied to the Terraform state resources."
  type        = map(string)

  default = {
    application         = "enterprise-policy-rag-benchmark"
    environment         = "shared"
    managed_by          = "terraform"
    purpose             = "terraform-state"
    data_classification = "internal"
  }
}
