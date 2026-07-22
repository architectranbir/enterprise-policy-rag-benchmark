#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <storage-account> <container> <immutable-run-id>" >&2
  exit 2
fi

account_name="$1"
container_name="$2"
run_id="$3"
if [[ ! "$account_name" =~ ^[a-z0-9]{3,24}$ ]] ||
   [[ ! "$container_name" =~ ^[a-z0-9-]{3,63}$ ]] ||
   [[ ! "$run_id" =~ ^[A-Za-z0-9._-]{8,128}$ ]]; then
  echo "Storage account, container or run ID has an invalid format" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
uv run --locked python "$repo_root/scripts/validate_benchmark_artifacts.py"
az storage blob upload-batch \
  --account-name "$account_name" \
  --auth-mode login \
  --destination "$container_name" \
  --destination-path "$run_id" \
  --source "$repo_root/benchmark_results" \
  --overwrite false \
  --no-progress
