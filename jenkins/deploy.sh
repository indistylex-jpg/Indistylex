#!/usr/bin/env bash
# Deploy Indistylex (Jenkins or manual). Re-run as root via sudo when needed.
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/html/indistylex}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${BRANCH:-develop}"
RUN_MIGRATIONS="${RUN_MIGRATIONS:-false}"
VENV_DIR="${VENV_DIR:-${APP_DIR}/venv}"

if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

log() { echo "[deploy] $*"; }

if [[ ! -d "${APP_DIR}/.git" ]]; then
  echo "ERROR: ${APP_DIR} is not a git repository" >&2
  exit 1
fi

cd "${APP_DIR}"

log "Fetching ${GIT_REMOTE}/${BRANCH}…"
git fetch "${GIT_REMOTE}" "${BRANCH}"
git checkout "${BRANCH}"
git pull "${GIT_REMOTE}" "${BRANCH}"

if [[ -f requirements.txt && -x "${VENV_DIR}/bin/pip" ]]; then
  log "Installing Python dependencies…"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
  pip install -r requirements.txt -q
fi

if [[ "${RUN_MIGRATIONS}" == "true" && -f .env ]]; then
  log "Running optional SQL migrations…"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
  if [[ -n "${DATABASE_URL:-}" && "${DATABASE_URL}" == mysql* ]]; then
    DB_PASS="${DB_PASSWORD:-${MYSQL_PASSWORD:-}}"
    if [[ -n "${DB_PASS}" ]]; then
      for sql in scripts/alter_product_age_groups_v2.sql scripts/create_expenses_table.sql; do
        if [[ -f "${sql}" ]]; then
          log "Applying ${sql} (ignore errors if already applied)…"
          mysql -u "${DB_USER:-indistylex}" -p"${DB_PASS}" indistylex < "${sql}" || true
        fi
      done
    else
      log "Skipping migrations — set DB_PASSWORD in .env or Jenkins credentials."
    fi
  fi
fi

log "Fixing permissions…"
${SUDO} chown -R www-data:www-data "${APP_DIR}"
${SUDO} chmod 600 "${APP_DIR}/.env" 2>/dev/null || true

log "Restarting indistylex service…"
${SUDO} systemctl restart indistylex
sleep 2

if ${SUDO} systemctl is-active --quiet indistylex; then
  log "Service is active."
else
  echo "ERROR: indistylex failed to start" >&2
  ${SUDO} journalctl -u indistylex --no-pager -n 30 >&2 || true
  exit 1
fi

if curl -sf --max-time 15 http://127.0.0.1:8000/ >/dev/null; then
  log "Health check passed (HTTP 200)."
else
  echo "WARNING: health check failed — service may still be starting." >&2
fi

log "Deploy complete: ${BRANCH} @ $(git rev-parse --short HEAD)"
