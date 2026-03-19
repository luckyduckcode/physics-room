#!/usr/bin/env bash
# Simple healthcheck that queries the local API and exits non-zero on failure
set -euo pipefail
URL=${1:-http://127.0.0.1:8000/health}
TIMEOUT=${2:-5}
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$URL" || true)
if [ "$HTTP_CODE" = "200" ]; then
  echo "OK"
  exit 0
else
  echo "Unhealthy: HTTP $HTTP_CODE"
  exit 1
fi
