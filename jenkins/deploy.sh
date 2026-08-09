#!/usr/bin/env bash
# Deploy Indistylex — used by Jenkins pipeline and manual server commands.
#
# Manual (no credentials needed on server if git remote is already configured):
#   cd /var/www/html/indistylex
#   ENVIRONMENT=staging ROLLOUT_ACTION=deploy bash jenkins/deploy.sh
#
# Rollback last deploy:
#   ROLLOUT_ACTION=rollback bash jenkins/deploy.sh
#
# Dry-run (show plan only):
#   ROLLOUT_ACTION=dry-run bash jenkins/deploy.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/environments.conf"

ENVIRONMENT="${ENVIRONMENT:-staging}"
ROLLOUT_ACTION="${ROLLOUT_ACTION:-deploy}"
GIT_REMOTE="${GIT_REMOTE:-shivam74826}"
RUN_MIGRATIONS="${RUN_MIGRATIONS:-false}"

if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

log() { echo "[deploy] $*"; }
die() { echo "[deploy] ERROR: $*" >&2; exit 1; }

resolve_environment() {
  case "${ENVIRONMENT}" in
    development|dev)
      BRANCH="${DEV_BRANCH}"
      APP_DIR="${APP_DIR:-/var/www/html/indistylex}"
      SERVICE="${STAGING_SERVICE}"
      HEALTH_URL="${STAGING_HEALTH_URL}"
      ;;
    staging|stage)
      BRANCH="${STAGING_BRANCH}"
      APP_DIR="${STAGING_APP_DIR}"
      SERVICE="${STAGING_SERVICE}"
      HEALTH_URL="${STAGING_HEALTH_URL}"
      ;;
    production|prod)
      BRANCH="${PRODUCTION_BRANCH}"
      APP_DIR="${PRODUCTION_APP_DIR}"
      SERVICE="${PRODUCTION_SERVICE}"
      HEALTH_URL="${PRODUCTION_HEALTH_URL}"
      ;;
    *)
      die "Unknown ENVIRONMENT=${ENVIRONMENT} (use development|staging|production)"
      ;;
  esac
  VENV_DIR="${VENV_DIR:-${APP_DIR}/venv}"
  HISTORY_FILE="${APP_DIR}/${DEPLOY_HISTORY_FILE}"
}

record_deploy() {
  local sha="$1"
  mkdir -p "$(dirname "${HISTORY_FILE}")"
  touch "${HISTORY_FILE}"
  if [[ -n "${sha}" ]]; then
    echo "${sha}" >> "${HISTORY_FILE}"
    tail -20 "${HISTORY_FILE}" > "${HISTORY_FILE}.tmp" && mv "${HISTORY_FILE}.tmp" "${HISTORY_FILE}"
  fi
}

previous_deploy_sha() {
  if [[ ! -f "${HISTORY_FILE}" ]]; then
    return 1
  fi
  local count
  count="$(wc -l < "${HISTORY_FILE}" | tr -d ' ')"
  if [[ "${count}" -lt 2 ]]; then
    return 1
  fi
  tail -2 "${HISTORY_FILE}" | head -1
}

git_sync() {
  log "Fetching ${GIT_REMOTE}/${BRANCH} in ${APP_DIR}…"
  cd "${APP_DIR}"
  git fetch "${GIT_REMOTE}" "${BRANCH}"
  git checkout "${BRANCH}"
  git pull "${GIT_REMOTE}" "${BRANCH}"
}

install_dependencies() {
  if [[ -f "${APP_DIR}/requirements.txt" && -x "${VENV_DIR}/bin/pip" ]]; then
    log "Installing Python dependencies…"
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
    pip install -r "${APP_DIR}/requirements.txt" -q
  else
    log "Skipping pip install (venv or requirements.txt missing)."
  fi
}

run_migrations() {
  if [[ "${RUN_MIGRATIONS}" != "true" ]]; then
    return 0
  fi
  if [[ ! -f "${APP_DIR}/.env" ]]; then
    log "Skipping migrations — no .env file."
    return 0
  fi
  log "Running optional SQL migrations…"
  set -a
  # shellcheck disable=SC1091
  source "${APP_DIR}/.env"
  set +a
  if [[ -n "${DATABASE_URL:-}" && "${DATABASE_URL}" == mysql* ]]; then
    DB_PASS="${DB_PASSWORD:-${MYSQL_PASSWORD:-}}"
    if [[ -n "${DB_PASS}" ]]; then
      for sql in scripts/alter_product_age_groups_v2.sql scripts/create_expenses_table.sql; do
        if [[ -f "${APP_DIR}/${sql}" ]]; then
          log "Applying ${sql} (ignore errors if already applied)…"
          mysql -u "${DB_USER:-indistylex}" -p"${DB_PASS}" indistylex < "${APP_DIR}/${sql}" || true
        fi
      done
    else
      log "Skipping migrations — DB_PASSWORD not set in .env."
    fi
  fi
}

fix_permissions() {
  log "Fixing permissions…"
  ${SUDO} chown -R www-data:www-data "${APP_DIR}"
  ${SUDO} chmod 600 "${APP_DIR}/.env" 2>/dev/null || true
  ${SUDO} chmod +x "${APP_DIR}/jenkins/"*.sh 2>/dev/null || true
}

restart_service() {
  log "Restarting ${SERVICE}…"
  ${SUDO} systemctl restart "${SERVICE}"
  sleep 2
  if ${SUDO} systemctl is-active --quiet "${SERVICE}"; then
    log "Service ${SERVICE} is active."
  else
    die "Service ${SERVICE} failed to start — run: journalctl -u ${SERVICE} -n 50"
  fi
}

action_dry_run() {
  resolve_environment
  log "DRY-RUN — no changes will be made"
  log "  Environment : ${ENVIRONMENT}"
  log "  Action      : ${ROLLOUT_ACTION}"
  log "  App dir     : ${APP_DIR}"
  log "  Branch      : ${BRANCH}"
  log "  Git remote  : ${GIT_REMOTE}"
  log "  Service     : ${SERVICE}"
  log "  Migrations  : ${RUN_MIGRATIONS}"
  if [[ -d "${APP_DIR}/.git" ]]; then
    cd "${APP_DIR}"
    log "  Current SHA : $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
    log "  Remote tip  : $(git rev-parse --short "${GIT_REMOTE}/${BRANCH}" 2>/dev/null || echo unknown)"
  fi
  if [[ -f "${HISTORY_FILE}" ]]; then
    log "  Last deploy : $(tail -1 "${HISTORY_FILE}" 2>/dev/null || echo none)"
    log "  Rollback to : $(previous_deploy_sha 2>/dev/null || echo unavailable)"
  fi
}

action_health_check() {
  resolve_environment
  bash "${SCRIPT_DIR}/health-check.sh" "${HEALTH_URL}" "${SERVICE}"
}

action_restart_only() {
  resolve_environment
  restart_service
  bash "${SCRIPT_DIR}/health-check.sh" "${HEALTH_URL}" "${SERVICE}"
  log "Restart-only complete."
}

action_rollback() {
  resolve_environment
  [[ -d "${APP_DIR}/.git" ]] || die "${APP_DIR} is not a git repository"

  PREV_SHA="$(previous_deploy_sha || true)"
  [[ -n "${PREV_SHA}" ]] || die "No previous deploy in ${HISTORY_FILE} — cannot rollback"

  log "Rolling back ${ENVIRONMENT} to ${PREV_SHA}…"
  cd "${APP_DIR}"
  git fetch "${GIT_REMOTE}" --tags
  git checkout "${PREV_SHA}"
  install_dependencies
  fix_permissions
  restart_service
  bash "${SCRIPT_DIR}/health-check.sh" "${HEALTH_URL}" "${SERVICE}"
  record_deploy "${PREV_SHA}"
  log "Rollback complete: ${PREV_SHA}"
}

action_deploy() {
  resolve_environment
  [[ -d "${APP_DIR}/.git" ]] || die "${APP_DIR} is not a git repository"

  CURRENT_SHA=""
  if [[ -d "${APP_DIR}/.git" ]]; then
    CURRENT_SHA="$(cd "${APP_DIR}" && git rev-parse HEAD 2>/dev/null || true)"
  fi

  git_sync
  NEW_SHA="$(git rev-parse HEAD)"
  install_dependencies
  run_migrations
  fix_permissions
  restart_service
  bash "${SCRIPT_DIR}/health-check.sh" "${HEALTH_URL}" "${SERVICE}"

  if [[ -n "${CURRENT_SHA}" && "${CURRENT_SHA}" != "${NEW_SHA}" ]]; then
    record_deploy "${CURRENT_SHA}"
  fi
  record_deploy "${NEW_SHA}"

  log "Deploy complete: ${ENVIRONMENT} @ ${NEW_SHA} (${BRANCH})"
}

main() {
  case "${ROLLOUT_ACTION}" in
    deploy)          action_deploy ;;
    rollback|roll-back) action_rollback ;;
    dry-run|dryrun) action_dry_run ;;
    restart-only|restart) action_restart_only ;;
    health-check|health) action_health_check ;;
    *)
      die "Unknown ROLLOUT_ACTION=${ROLLOUT_ACTION} (use deploy|rollback|dry-run|restart-only|health-check)"
      ;;
  esac
}

main "$@"
