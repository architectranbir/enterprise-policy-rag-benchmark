resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "text-embedding-3-large"
  cognitive_account_id = azurerm_cognitive_account.foundry.id

  version_upgrade_option = "NoAutoUpgrade"

  model {
    format  = "OpenAI"
    name    = "text-embedding-3-large"
    version = "1"
  }

  sku {
    name     = "Standard"
    capacity = 1
  }
}

resource "azurerm_cognitive_deployment" "answer" {
  count                = var.deploy_application_platform ? 1 : 0
  name                 = var.answer_model_name
  cognitive_account_id = azurerm_cognitive_account.foundry.id

  version_upgrade_option = "NoAutoUpgrade"

  model {
    format  = "OpenAI"
    name    = var.answer_model_name
    version = var.answer_model_version
  }

  sku {
    name     = "GlobalStandard"
    capacity = var.answer_model_capacity
  }
}
