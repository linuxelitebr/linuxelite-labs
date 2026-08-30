#!/usr/bin/env bash
# Hit each scenario and show the status line plus the header the RFC requires.
# Start the origin first (node server.js).
#
#   ./demo.sh

set -euo pipefail
BASE="${1:-http://localhost:8080}"

show() { curl -sD - -o /dev/null "$@" | grep -iE '^(HTTP|WWW-Authenticate|Allow|Proxy-Authenticate|Content-Type)' | tr -d '\r'; echo; }

echo "=== 401 needs-auth (WWW-Authenticate MUST) ===";  show "$BASE/needs-auth"
echo "=== 403 forbidden (no WWW-Authenticate) ===";     show "$BASE/forbidden"
echo "=== 404 hidden (a forbidden resource, hidden) ==="; show "$BASE/hidden"
echo "=== 405 only-get via POST (Allow MUST) ===";      show -X POST "$BASE/only-get"
echo "=== 407 via-proxy (Proxy-Authenticate MUST) ==="; show "$BASE/via-proxy"
echo "=== 400 bad-request ===";                         show "$BASE/bad-request"
