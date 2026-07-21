provider "azurerm" {
  features {}

  subscription_id     = var.subscription_id
  storage_use_azuread = true

  resource_provider_registrations = "none"

  resource_providers_to_register = [
    "Microsoft.CognitiveServices",
    "Microsoft.App",
    "Microsoft.ContainerRegistry",
    "Microsoft.DBforPostgreSQL",
    "Microsoft.Insights",
    "Microsoft.KeyVault",
    "Microsoft.ManagedIdentity",
    "Microsoft.Resources",
    "Microsoft.Search",
    "Microsoft.Web",
  ]
}
