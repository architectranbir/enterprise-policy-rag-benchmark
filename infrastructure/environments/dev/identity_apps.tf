data "azuread_client_config" "current" {}

resource "random_uuid" "policy_read_scope" {}

resource "azuread_application" "api" {
  count                   = var.deploy_application_platform ? 1 : 0
  display_name            = "Enterprise Policy RAG API (${var.environment})"
  description             = "Protected API for the Enterprise Policy RAG benchmark."
  identifier_uris         = ["api://enterprise-policy-rag-benchmark-${var.environment}"]
  owners                  = [data.azuread_client_config.current.object_id]
  sign_in_audience        = "AzureADMyOrg"
  group_membership_claims = ["SecurityGroup"]
  prevent_duplicate_names = true

  api {
    requested_access_token_version = 2

    oauth2_permission_scope {
      admin_consent_description  = "Allow the Web UI to ask questions against authorised policy evidence."
      admin_consent_display_name = "Read authorised policy answers"
      enabled                    = true
      id                         = random_uuid.policy_read_scope.result
      type                       = "User"
      user_consent_description   = "Allow this application to retrieve policy answers you are authorised to access."
      user_consent_display_name  = "Read your authorised policy answers"
      value                      = "Policy.Read"
    }
  }
}

resource "azuread_service_principal" "api" {
  count     = var.deploy_application_platform ? 1 : 0
  client_id = azuread_application.api[0].client_id
  owners    = [data.azuread_client_config.current.object_id]
}

resource "azuread_application" "web" {
  count                   = var.deploy_application_platform ? 1 : 0
  display_name            = "Enterprise Policy RAG Web (${var.environment})"
  description             = "Single-page Web UI for the Enterprise Policy RAG benchmark."
  owners                  = [data.azuread_client_config.current.object_id]
  sign_in_audience        = "AzureADMyOrg"
  prevent_duplicate_names = true

  single_page_application {
    redirect_uris = [
      "https://${azurerm_static_web_app.web[0].default_host_name}/",
      "http://localhost:8080/",
    ]
  }

  required_resource_access {
    resource_app_id = azuread_application.api[0].client_id

    resource_access {
      id   = random_uuid.policy_read_scope.result
      type = "Scope"
    }
  }
}

resource "azuread_service_principal" "web" {
  count     = var.deploy_application_platform ? 1 : 0
  client_id = azuread_application.web[0].client_id
  owners    = [data.azuread_client_config.current.object_id]
}

resource "azuread_group" "policy_employees" {
  count                   = var.deploy_application_platform ? 1 : 0
  display_name            = "Enterprise Policy RAG Employees (${var.environment})"
  description             = "Users authorised for the synthetic employees policy corpus."
  owners                  = [data.azuread_client_config.current.object_id]
  members                 = [data.azuread_client_config.current.object_id]
  security_enabled        = true
  prevent_duplicate_names = true
}
