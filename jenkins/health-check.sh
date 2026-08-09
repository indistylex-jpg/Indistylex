#!/usr/bin/env bash
# Health check after deploy. Exit 0 = healthy.
set -euo pipefail

HEALTH_URL="${1:-http://127.0.0.1:8000/}"
SERVICE_NAME="${2:-indistylex}"
MAX_ATTEMPTS="${3:-6}"
SLEEP_SEC="${4:-5}"

log() { echo "[health] $*"; }

if ! systemctl is-active --quiet "${SERVICE_NAME}" 2>/dev/null; then
  log "FAIL: systemd service ${SERVICE_NAME} is not active"
  systemctl status "${SERVICE_NAME}" --no-pager -l 2>/dev/null || true
  exit 1
fi

for attempt in $(seq 1 "${MAX_ATTEMPTS}"); do
  if curl -sf --max-time 15 "${HEALTH_URL}" >/dev/null; then
    log "OK: ${HEALTH_URL} returned HTTP 200 (attempt ${attempt}/${MAX_ATTEMPTS})"
    exit 0
  fi
  log "Waiting for ${HEALTH_URL}… (${attempt}/${MAX_ATTEMPTS})"
  sleep "${SLEEP_SEC}"
done

log "FAIL: ${HEALTH_URL} did not respond with HTTP 200"
exit 1
