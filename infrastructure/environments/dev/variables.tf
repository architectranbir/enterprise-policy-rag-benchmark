variable "subscription_id" {
  description = "Azure subscription ID for the development environment."
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

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
  nullable    = false

  validation {
    condition     = var.environment == "dev"
    error_message = "This Terraform root is reserved for the dev environment."
  }
}

variable "location" {
  description = "Azure region for development resources."
  type        = string
  default     = "uksouth"
  nullable    = false

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must not be empty."
  }
}

variable "location_short" {
  description = "Short region code used in resource names."
  type        = string
  default     = "uks"
  nullable    = false

  validation {
    condition = can(
      regex("^[a-z0-9]{2,6}$", var.location_short)
    )
    error_message = "location_short must contain 2 to 6 lowercase letters or numbers."
  }
}

variable "workload_name" {
  description = "Short workload name used in Azure resource names."
  type        = string
  default     = "polrag"
  nullable    = false

  validation {
    condition = can(
      regex("^[a-z0-9]{3,12}$", var.workload_name)
    )
    error_message = "workload_name must contain 3 to 12 lowercase letters or numbers."
  }
}

variable "instance_number" {
  description = "Three-digit deployment instance number."
  type        = string
  default     = "001"
  nullable    = false

  validation {
    condition = can(
      regex("^[0-9]{3}$", var.instance_number)
    )
    error_message = "instance_number must contain exactly three digits."
  }
}

variable "unique_suffix" {
  description = "Six-character suffix for globally unique Azure resource names."
  type        = string
  nullable    = false

  validation {
    condition = can(
      regex("^[a-z0-9]{6}$", var.unique_suffix)
    )
    error_message = "unique_suffix must contain exactly six lowercase letters or numbers."
  }
}

variable "tags" {
  description = "Common tags applied to development resources."
  type        = map(string)

  default = {
    application         = "enterprise-policy-rag-benchmark"
    environment         = "dev"
    managed_by          = "terraform"
    data_classification = "internal"
    workload            = "policy-intelligence"
  }
}
