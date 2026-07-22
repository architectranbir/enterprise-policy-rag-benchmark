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

variable "deploy_application_platform" {
  description = "Whether to provision the optional application hosting and data platform."
  type        = bool
  default     = false
}

variable "vector_backend" {
  description = "Retrieval backend configured in the deployed API Container App."
  type        = string
  default     = "azure_ai_search"
  nullable    = false

  validation {
    condition     = contains(["azure_ai_search", "pgvector", "qdrant"], var.vector_backend)
    error_message = "vector_backend must be azure_ai_search, pgvector or qdrant."
  }
}

variable "enable_private_endpoints" {
  description = "Whether to provision private endpoints and deny unrestricted public data-plane access."
  type        = bool
  default     = false
  nullable    = false
}

variable "operator_ip_ranges" {
  description = "Reviewed public CIDRs allowed for operator data-plane access during development; keep empty for private-only access."
  type        = set(string)
  default     = []
  nullable    = false

  validation {
    condition = alltrue([
      for cidr in var.operator_ip_ranges : can(cidrhost(cidr, 0))
    ])
    error_message = "operator_ip_ranges entries must be valid IPv4 or IPv6 CIDRs."
  }
}

variable "qdrant_secret_rotation_version" {
  description = "Increment to create new write-only Qdrant admin and read-only Key Vault secret versions."
  type        = number
  default     = 1
  nullable    = false

  validation {
    condition     = var.qdrant_secret_rotation_version >= 1 && floor(var.qdrant_secret_rotation_version) == var.qdrant_secret_rotation_version
    error_message = "qdrant_secret_rotation_version must be a positive integer."
  }
}

variable "enable_postgres_bootstrap" {
  description = "Temporarily provision a VNet-scoped PostgreSQL Entra administrator job for least-privilege role bootstrap. Disable immediately after a successful run."
  type        = bool
  default     = false
  nullable    = false
}

variable "tenant_id" {
  description = "Microsoft Entra tenant ID for Key Vault and PostgreSQL authentication."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition = (
      !var.deploy_application_platform ||
      (
        var.tenant_id != null &&
        can(regex("^[0-9a-fA-F-]{36}$", var.tenant_id))
      )
    )
    error_message = "tenant_id must be supplied as a GUID when deploy_application_platform is true."
  }
}

variable "answer_model_name" {
  description = "GA Foundry model used for grounded answer generation."
  type        = string
  default     = "gpt-5.6-sol"
}

variable "answer_model_version" {
  description = "Pinned GA Foundry answer-model version."
  type        = string
  default     = "2026-07-09"
}

variable "answer_model_capacity" {
  description = "Global Standard capacity assigned to the answer-model deployment."
  type        = number
  default     = 1

  validation {
    condition     = var.answer_model_capacity >= 1
    error_message = "answer_model_capacity must be at least 1."
  }
}

variable "postgres_entra_administrator_name" {
  description = "Display/login name of the reviewed Microsoft Entra PostgreSQL administrator."
  type        = string
  default     = null
  nullable    = true
}

variable "postgres_entra_administrator_object_id" {
  description = "Object ID of the reviewed Microsoft Entra PostgreSQL administrator."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition = (
      !var.deploy_application_platform ||
      (var.postgres_entra_administrator_object_id != null && can(regex("^[0-9a-fA-F-]{36}$", var.postgres_entra_administrator_object_id)))
    )
    error_message = "postgres_entra_administrator_object_id must be a GUID when the platform is deployed."
  }
}

variable "api_container_image" {
  description = "Immutable API container image reference."
  type        = string
  default     = ""

  validation {
    condition = (
      !var.deploy_application_platform ||
      length(trimspace(var.api_container_image)) > 0
    )
    error_message = "api_container_image is required when deploy_application_platform is true."
  }
}

variable "ingestion_container_image" {
  description = "Optional immutable ingestion and benchmark job image; defaults to the API image."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition = (
      var.ingestion_container_image == null ||
      can(regex("@sha256:[0-9a-f]{64}$", var.ingestion_container_image))
    )
    error_message = "ingestion_container_image must be an immutable sha256 image reference."
  }
}

variable "qdrant_container_image" {
  description = "Pinned Qdrant demo image."
  type        = string
  default     = "qdrant/qdrant:v1.18.2"
}
