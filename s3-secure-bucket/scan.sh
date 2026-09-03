#!/usr/bin/env bash
# Prove the bucket is hardened without an AWS account. checkov reads the .tf
# files statically and checks them against its S3 policy pack. No credentials,
# no terraform apply, no cost.
set -euo pipefail

if ! command -v checkov >/dev/null 2>&1; then
  echo "checkov not found. Install it with: pip install checkov"
  exit 1
fi

cd "$(dirname "$0")"
checkov -d . --compact
