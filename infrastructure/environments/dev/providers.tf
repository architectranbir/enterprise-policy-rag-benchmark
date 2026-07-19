provider "azurerm" {
  features {}

  subscription_id     = var.subscription_id
  storage_use_azuread = true

  resource_provider_registrations = "none"

  resource_providers_to_register = [
    "Microsoft.CognitiveServices",
    "Microsoft.ManagedIdentity",
    "Microsoft.Resources",
    "Microsoft.Search",
  ]
}
