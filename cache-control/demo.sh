#!/usr/bin/env bash
# Hit every endpoint and show the Cache-Control header it emits.
# Start the origin first (node server.js). Point it at Varnish (port 8081) to watch the
# shared cache do its thing: repeat the call and look at X-Cache and Age.
#
#   ./demo.sh                       # hit the origin (8080)
#   ./demo.sh http://localhost:8081 # hit Varnish (shared cache)

set -euo pipefail
BASE="${1:-http://localhost:8080}"

echo "target: $BASE"
echo

for path in /static /api /secret /mixed /swr; do
  echo "=== $path ==="
  curl -sI "$BASE$path" | grep -iE '^(HTTP|Cache-Control|Age|X-Cache)' || true
  echo
done
