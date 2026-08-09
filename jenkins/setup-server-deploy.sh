#!/usr/bin/env bash
# One-time server setup so deploy works WITHOUT entering git credentials.
# Run on production server as root:
#   cd /var/www/html/indistylex && bash jenkins/setup-server-deploy.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/html/indistylex}"
GIT_REMOTE="${GIT_REMOTE:-shivam74826}"
STAGING_BRANCH="${STAGING_BRANCH:-develop}"

log() { echo "[setup-server] $*"; }
die() { echo "[setup-server] ERROR: $*" >&2; exit 1; }

[[ "${EUID}" -eq 0 ]] || die "Run as root: sudo bash jenkins/setup-server-deploy.sh"

log "App directory: ${APP_DIR}"
[[ -d "${APP_DIR}/.git" ]] || die "${APP_DIR} is not a git repo — clone Indistylex first."

cd "${APP_DIR}"

log "Ensuring deploy scripts are executable…"
chmod +x jenkins/*.sh

log "Creating deploy history file…"
touch "${APP_DIR}/.deploy-history"
chown www-data:www-data "${APP_DIR}/.deploy-history" 2>/dev/null || true
echo "$(git rev-parse HEAD 2>/dev/null || echo unknown)" >> "${APP_DIR}/.deploy-history"
sort -u "${APP_DIR}/.deploy-history" -o "${APP_DIR}/.deploy-history" || true

log "Checking git remote '${GIT_REMOTE}'…"
if ! git remote get-url "${GIT_REMOTE}" >/dev/null 2>&1; then
  log "Adding remote ${GIT_REMOTE} → https://github.com/shivam74826/Indistylex.git"
  git remote add "${GIT_REMOTE}" "https://github.com/shivam74826/Indistylex.git" 2>/dev/null || \
    git remote set-url "${GIT_REMOTE}" "https://github.com/shivam74826/Indistylex.git"
fi

log "Testing passwordless git pull (${GIT_REMOTE}/${STAGING_BRANCH})…"
export GIT_TERMINAL_PROMPT=0
if git fetch "${GIT_REMOTE}" "${STAGING_BRANCH}" 2>/dev/null; then
  log "OK: git fetch works without credentials."
else
  cat <<'EOF'

⚠️  Git fetch needs credentials. Fix ONE of these on the server:

Option A — SSH deploy key (recommended):
  ssh-keygen -t ed25519 -f /root/.ssh/indistylex_deploy -N ""
  cat /root/.ssh/indistylex_deploy.pub
  → Add as Deploy key in GitHub repo: Settings → Deploy keys → Read-only

  git remote set-url shivam74826 git@github.com:shivam74826/Indistylex.git
  GIT_SSH_COMMAND='ssh -i /root/.ssh/indistylex_deploy -o IdentitiesOnly=yes' git fetch shivam74826 develop

Option B — HTTPS credential store (one-time token):
  git config credential.helper store
  git pull shivam74826 develop   # enter GitHub token once; stored in ~/.git-credentials

EOF
  die "Configure git access then re-run this script."
fi

log "Configuring sudoers for passwordless deploy…"
cat > /etc/sudoers.d/indistylex-deploy <<SUDOERS
# Indistylex deploy user — Jenkins SSH (minimal sudo)
indistylex-deploy ALL=(root) NOPASSWD: /bin/systemctl restart indistylex
indistylex-deploy ALL=(root) NOPASSWD: /bin/systemctl status indistylex
indistylex-deploy ALL=(root) NOPASSWD: /bin/systemctl is-active indistylex
indistylex-deploy ALL=(root) NOPASSWD: /bin/chown -R www-data\:www-data ${APP_DIR}
indistylex-deploy ALL=(root) NOPASSWD: /bin/chmod 600 ${APP_DIR}/.env
SUDOERS
chmod 440 /etc/sudoers.d/indistylex-deploy
visudo -cf /etc/sudoers.d/indistylex-deploy

log "Ensuring deploy user exists and can write to app dir…"
id indistylex-deploy >/dev/null 2>&1 || useradd -m -s /bin/bash indistylex-deploy
usermod -aG www-data indistylex-deploy
chmod -R g+rwX "${APP_DIR}"
find "${APP_DIR}" -type d -exec chmod g+s {} \;

log "Fixing app ownership…"
chown -R www-data:www-data "${APP_DIR}"
chmod 600 "${APP_DIR}/.env" 2>/dev/null || true

cat <<EOF

==============================================
 Server deploy setup complete.
==============================================

Manual deploy (no credentials prompt after git is configured):

  cd ${APP_DIR}
  git pull ${GIT_REMOTE} ${STAGING_BRANCH}
  systemctl restart indistylex

Or use the deploy script:

  ENVIRONMENT=staging ROLLOUT_ACTION=deploy bash jenkins/deploy.sh

Rollback:

  ENVIRONMENT=staging ROLLOUT_ACTION=rollback bash jenkins/deploy.sh

Dry-run:

  ENVIRONMENT=production ROLLOUT_ACTION=dry-run bash jenkins/deploy.sh

EOF
