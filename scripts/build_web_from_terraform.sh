#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd "${script_dir}/.." && pwd)"
terraform_directory="${1:-${repository_root}/infrastructure/environments/dev}"

terraform_output() {
  terraform -chdir="${terraform_directory}" output -raw "$1"
}

export VITE_ENTRA_TENANT_ID="$(terraform_output entra_tenant_id)"
export VITE_ENTRA_WEB_CLIENT_ID="$(terraform_output entra_web_client_id)"
export VITE_ENTRA_API_SCOPE="$(terraform_output entra_api_scope)"
export VITE_API_BASE_URL="https://$(terraform_output api_fqdn)"

npm --prefix "${repository_root}/web" ci
npm --prefix "${repository_root}/web" run build
